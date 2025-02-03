import os
from openai import OpenAI

base_url="https://api-llm.ml.ptsecurity.ru/v1"
model = "positive-llm-chat"


diff_str = '''
diff --git a/example/example.cc b/example/example.cc
new file mode 100644
index 0000000..0f44432
--- /dev/null
+++ b/example/example.cc
@@ -0,0 +1,15 @@
+#include <ldapi_detector.hh>
+#include <iostream>
+
+int main()
+{
+    // CPP интерфейс
+    std::string str("example.com\",OU=Secret,DC=testlab,DC=\"zzzz\\\"zzz)\x00");
+    ptaf::grammar::ldap::LdapiDetector detector;
+    auto has_attack = detector.isInjection(str);
+    auto is_parsed = detector.isParsed(str);
+
+    std::cout << "str :\"" << str << "\"\n";
+    std::cout << "has_attack : " << has_attack << "\n";
+    std::cout << "is_parsed : " << is_parsed << "\n";
+}
diff --git a/src/DetectDriver.cc b/src/DetectDriver.cc
deleted file mode 100644
index d2ef50e..0000000
--- a/src/DetectDriver.cc
+++ /dev/null
@@ -1,237 +0,0 @@
-/*
-Positive Library for detect injection by contexts (Positive Technologies)
-The MIT license (MIT).
-Copyright (c) 2018-2020, Positive Technologies
-
-Permission is hereby granted, free of charge, to any person obraining a copy
-of this software and associated documentation files (the "Software"), to deal
-in the Software without restriction, including without limitation the rights
-to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-copies of the Software, and to permit persons to whom the Software is
-furnished to do so, subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included
-in all copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
-THE SOFTWARE.
-*/
-#define DEBUG_OUTPUT
-#undef DEBUG_OUTPUT
-
-#ifdef DEBUG_OUTPUT
-#include <iostream>
-#endif
-
-#include <string>
-
-#include "LdapCommon.hh"
-#include "DetectDriver.hh"
-
-
-namespace ptaf::grammar::ldap {
-
-    static struct ptaf::grammar::ldap::ContextDescriptor baseCtxs[] = {
-        {
-            2 /* id */
-            , "(&(a=" /* prefix */
-            , ")(b=const))" /* postfix */
-            , 5 /* prefixTokensCount */
-            , 7 /* postfixTokensCount */
-            , ptaf::grammar::ldap::ContextFeature::BRACE /* features */
-            , 4 /* contextForbiddenCount */
-            , 0 /* contextSpecForbiddenCount */
-        }
-        ,{
-            4 /* id */
-            , "(|(&(a=" /* prefix */
-            , ")(b=const)))" /* postfix */
-            , 8 /* prefixTokensCount */
-            , 8 /* postfixTokensCount */
-            , ptaf::grammar::ldap::ContextFeature::BRACE /* features */
-            , 6 /* contextForbiddenCount */
-            , 0 /* contextSpecForbiddenCount */
-        }
-        ,{
-            5 /* id */
-            , "(a=b=" /* prefix */
-            , ")" /* postfix */
-            , 4 /* prefixTokensCount */
-            , 1 /* postfixTokensCount */
-            , ptaf::grammar::ldap::ContextFeature::BRACE /* features */
-            , 1 /* contextForbiddenCount */
-            , 0 /* contextSpecForbiddenCount */
-        }
-        ,{
-            6 /* id */
-            , "(|((a=" /* prefix */
-            , ")))" /* postfix */
-            , 6 /* prefixTokensCount */
-            , 3 /* postfixTokensCount */
-            , ptaf::grammar::ldap::ContextFeature::BRACE
-                | ptaf::grammar::ldap::ContextFeature::DBRACE /* features */
-            , 4 /* contextForbiddenCount */
-            , 0 /* contextSpecForbiddenCount */
-        }
-    };
-    static struct ptaf::grammar::ldap::ContextDescriptor quoteCtxs[] = {
-        {
-            7 /* id */
-            , "(a=b=\"" /* prefix */
-            , ")" /* postfix */
-            , 4 /* prefixTokensCount */
-            , 1 /* postfixTokensCount */
-            , ptaf::grammar::ldap::ContextFeature::DQUOTE
-                | ptaf::grammar::ldap::ContextFeature::BRACE /* features */
-            , 1 /* contextForbiddenCount */
-            , 0 /* contextSpecForbiddenCount */
-        }
-        ,{
-            8 /* id */
-            , "(a=b=\"" /* prefix */
-            , "\")" /* postfix */
-            , 4 /* prefixTokensCount */
-            , 1 /* postfixTokensCount */
-            , ptaf::grammar::ldap::ContextFeature::DQUOTE
-                | ptaf::grammar::ldap::ContextFeature::BRACE /* features */
-            , 1 /* contextForbiddenCount */
-            , 0 /* contextSpecForbiddenCount */
-        }
-    };
-    static bool isEmptyVector(std::string& vector)
-    {
-        for(auto nextCh = vector.begin(); nextCh != vector.end(); ++nextCh) {
-            if(*nextCh != ' ' && *nextCh != '\t' && *nextCh != '\n' && *nextCh != '\r') {
-                return 0;
-            }
-        }
-        return 1;
-    }
-    static int getVectorFeatures(std::string& vector)
-    {
-        int features = ptaf::grammar::ldap::ContextFeature::NONE;
-        int cntBraces = 0;
-        for(auto nextCh = vector.begin(); nextCh != vector.end(); ++nextCh) {
-            switch(*nextCh) {
-                case ')':
-                    ++cntBraces;
-                    break;
-                case '"':
-                    features |= ptaf::grammar::ldap::ContextFeature::DQUOTE;
-                    break;
-            }
-        }
-        switch(cntBraces) {
-            case 0:
-                break;
-            case 1:
-                features |= ptaf::grammar::ldap::ContextFeature::BRACE;
-                break;
-            default:
-                features |= (
-                    ptaf::grammar::ldap::ContextFeature::BRACE
-                    | ptaf::grammar::ldap::ContextFeature::DBRACE
-                );
-        }
-        return features;
-    }
-} /* namespace ptaf::grammar::ldap */
-
-ptaf::grammar::ldap::DetectDriver::DetectDriver(ptaf::grammar::LdapLexer *lex)
-    : lexer_(lex), parser_(lex)
-{
-    this->tokensCount_ = 0;
-    this->forbiddenNodeCount_ = 0;
-    this->specForbiddenNodeCount_ = 0;
-}
-
-std::string ptaf::grammar::ldap::DetectDriver::version()
-{
-    return std::string("1.4-2");
-}
-
-bool ptaf::grammar::ldap::DetectDriver::isInjection(std::string &vector)
-{
-    /* If string is empty, then there is no injection */
-    if(ptaf::grammar::ldap::isEmptyVector(vector)) {
-        return 0;
-    }
-    int vectorFeatures = ptaf::grammar::ldap::getVectorFeatures(vector);
-#ifdef DEBUG_OUTPUT
-    std::cout << "DEBUG. Check vector <--" << vector << "--> with features = " << vectorFeatures << std::endl;
-#endif
-    bool hasInjection = this->checkContexts(vector, vectorFeatures, ptaf::grammar::ldap::baseCtxs);
-    if(!hasInjection && (vectorFeatures&ptaf::grammar::ldap::ContextFeature::DQUOTE)) {
-        hasInjection = this->checkContexts(vector, vectorFeatures, ptaf::grammar::ldap::quoteCtxs);
-    }
-    return hasInjection;
-}
-
-
-template <size_t N>
-bool ptaf::grammar::ldap::DetectDriver::checkContexts(
-    std::string &vector,
-    int vectorFeatures,
-    const struct ptaf::grammar::ldap::ContextDescriptor (&ctxs)[N]
-) {
-    for (auto ctx : ctxs) {
-        /* Filter context base on vector's features */
-#ifdef DEBUG_OUTPUT
-        std::cout << "\tContext with id " << ctx.id << std::endl;
-#endif
-        if((ctx.features & vectorFeatures) != ctx.features) {
-#ifdef DEBUG_OUTPUT
-            std::cout << "\t\tFeatures not match" << std::endl;
-#endif
-            continue;
-        }
-        std::string vectorLdap = ctx.prefix + vector + ctx.postfix;
-        reflex::Input inVector(vectorLdap);
-        if (!isParsed(inVector, &ctx)) {
-#ifdef DEBUG_OUTPUT
-            std::cout << "\t\tVector not parsed with this context" << std::endl;
-#endif
-            continue;
-        }
-#ifdef DEBUG_OUTPUT
-            std::cout << "\t\tVector successfully PARSED! vector: <--" << vectorLdap << "-->" << std::endl;
-#endif
-        if(
-            this->forbiddenNodeCount_ > ctx.contextForbiddenCount
-            ||
-            this->specForbiddenNodeCount_ > ctx.contextSpecForbiddenCount
-        ) {
-#ifdef DEBUG_OUTPUT
-            std::cout << "\t\tFOUND INJECTION! forbidden = " << this->forbiddenNodeCount_
-                << ", spec forbidden = " << this->specForbiddenNodeCount_ << std::endl;
-#endif
-            return 1; /* INJECTION */
-        }
-    }
-#ifdef DEBUG_OUTPUT
-    std::cout << "\tInjection not found: vector is CLEAR";
-#endif
-    return 0 /* Injection not found */;
-}
-
-bool ptaf::grammar::ldap::DetectDriver::isParsed(
-    reflex::Input &vector, ptaf::grammar::ldap::ContextDescriptor * ctxDescr
-) {
-    // Initialize lexer with new vector
-    this->lexer_->reInit(vector, ctxDescr);
-    /*
-     * parser->parse() return 0 if successfully parsed,
-     *  but we return True if successfull parsed and False - else
-    */
-    bool isParse = !(this->parser_.parse());
-    // save count of tokens after parsing vector
-    this->tokensCount_ = this->lexer_->tokensCount();
-    this->forbiddenNodeCount_ = this->lexer_->forbiddenNodeCount();
-    this->specForbiddenNodeCount_ = this->lexer_->specForbiddenNodeCount();
-    return isParse;
-}
diff --git a/src/LdapiDetector.cc b/src/LdapiDetector.cc
deleted file mode 100644
index 41d1c1f..0000000
--- a/src/LdapiDetector.cc
+++ /dev/null
@@ -1,75 +0,0 @@
-#include "LdapiDetector.hh"
-#include "LdapCommon.hh"
-#include "DetectDriver.hh"
-
-#include <string>
-
-namespace ptaf::grammar::ldap {
-    static ptaf::grammar::ldap::ContextDescriptor default_ctx_descriptor = {
-        0 /* id */
-        , "" /* prefix */
-        , "" /* postfix */
-        , 0 /* prefixTokensCount */
-        , 0 /* postfixTokensCount */
-        , ptaf::grammar::ldap::ContextFeature::NONE /* features */
-        , 0 /* contextForbiddenCount */
-        , 0 /* contextSpecForbiddenCount */
-    };
-}
-
-class LdapiDetector::LdapiTools {
-    friend class LdapiDetector;
-    using lexer_t = ptaf::grammar::LdapLexer;
-    using detector_t = ptaf::grammar::ldap::DetectDriver;
-    using ctx_descr_t = ptaf::grammar::ldap::ContextDescriptor;
-
-public:
-    LdapiTools() :
-        ctx_descriptor_(ptaf::grammar::ldap::default_ctx_descriptor),
-        lexer_(&this->ctx_descriptor_, std::string("ldap init")),
-        detector_(&lexer_) {}
-
-private:
-    ctx_descr_t ctx_descriptor_;
-    lexer_t lexer_;
-    detector_t detector_;
-};
-
-LdapiDetector::LdapiDetector() :
-    ldapi_(std::make_unique<LdapiTools>()) {}
-
-LdapiDetector::~LdapiDetector() {}
-
-bool LdapiDetector::isInjection(std::string_view data) const
-{
-    std::string vector(data);
-    return ldapi_->detector_.isInjection(vector);
-}
-
-bool LdapiDetector::isParsed(std::string_view data) const
-{
-    reflex::Input vector(data.data(), data.size());
-    return ldapi_->detector_.isParsed(vector, &ldapi_->ctx_descriptor_);
-}
-
-std::string LdapiDetector::version() const
-{
-    return ldapi_->detector_.version();
-}
-
- int LdapiDetector::lastparseTokensCount() const
- {
-     return ldapi_->detector_.lastparseTokensCount();
- }
-
-int LdapiDetector::lastparseForbiddenCount() const
-{
-    return ldapi_->detector_.lastparseForbiddenCount();
-}
-
-int LdapiDetector::lastparseSpecForbiddenCount() const
-{
-    return ldapi_->detector_.lastparseSpecForbiddenCount();
-}
-
-
diff --git a/src/LdapiDetector.hh b/src/LdapiDetector.hh
deleted file mode 100644
index f9a154c..0000000
--- a/src/LdapiDetector.hh
+++ /dev/null
@@ -1,30 +0,0 @@
-#pragma once
-
-#include <string_view>
-#include <memory>
-
-#pragma GCC visibility push(default)
-
-class LdapiDetector {
-public:
-    LdapiDetector();
-    ~LdapiDetector();
-
-    bool isInjection(std::string_view data) const;
-
-    bool isParsed(std::string_view data) const;
-
-    std::string version() const;
-
-    int lastparseTokensCount() const;
-
-    int lastparseForbiddenCount() const;
-
-    int lastparseSpecForbiddenCount() const;
-
-private:
-    class LdapiTools;
-    std::unique_ptr<LdapiTools> ldapi_;
-};
-
-#pragma GCC visibility pop
diff --git a/src/detect_driver.cc b/src/detect_driver.cc
new file mode 100644
index 0000000..b169eca
--- /dev/null
+++ b/src/detect_driver.cc
@@ -0,0 +1,232 @@
+#include "detect_driver.hh"
+#include <format>
+#include <string>
+#include "detectors-api/common/simd_helpers.hh"
+#include "ldap_common.hh"
+
+#ifdef DEBUG
+#define DEBUG_LOG(x) std::cout << "DEBUG: " << __FILE__ << ":" << __LINE__ << " " << x << "\n"
+#else
+#define DEBUG_LOG(x)
+#endif
+
+namespace {
+
+// построим битовую матрицу для поиска символов
+auto simd_bitmap = detectos_common::simd::build_chars_bitmap(")\"");
+/* Функция будет вызвана для всех найденных символов.
+ * На вход она принимает текущий символ и счетчик для накопления
+ * количества скобок.
+ */
+int check_context_feature(char ch, size_t &braces_count)
+{
+    using ptaf::grammar::ldap::ContextFeature;
+    ContextFeature feature = ContextFeature::NONE;
+    switch (ch) {
+        case '"':
+            feature = ContextFeature::DQUOTE;
+            break;
+        case ')':
+            ++braces_count;
+            break;
+    }
+    if (braces_count) {
+        if (braces_count == 1) {
+            feature |= ContextFeature::BRACE;
+        } else {
+            feature |= (ContextFeature::BRACE | ContextFeature::DBRACE);
+        }
+    }
+    return static_cast<int>(feature);
+}
+
+constexpr std::string_view trim_spaces_left(std::string_view vector)
+{
+    vector.remove_prefix(std::min(vector.find_first_not_of(" \t"), vector.size()));
+
+    return vector;
+}
+}  // namespace
+
+namespace ptaf::grammar::ldap {
+
+constexpr static std::array BASE_CONTEXTS = {
+    ContextDescriptor{
+        2 /* id */
+        ,
+        "(&(a=" /* prefix */
+        ,
+        ")(b=const))" /* postfix */
+        ,
+        5 /* prefixTokensCount */
+        ,
+        7 /* postfixTokensCount */
+        ,
+        ContextFeature::BRACE /* features */
+        ,
+        4 /* contextForbiddenCount */
+        ,
+        0 /* contextSpecForbiddenCount */
+    },
+    ContextDescriptor{
+        4 /* id */
+        ,
+        "(|(&(a=" /* prefix */
+        ,
+        ")(b=const)))" /* postfix */
+        ,
+        8 /* prefixTokensCount */
+        ,
+        8 /* postfixTokensCount */
+        ,
+        ContextFeature::BRACE /* features */
+        ,
+        6 /* contextForbiddenCount */
+        ,
+        0 /* contextSpecForbiddenCount */
+    },
+    ContextDescriptor{
+        5 /* id */
+        ,
+        "(a=b=" /* prefix */
+        ,
+        ")" /* postfix */
+        ,
+        4 /* prefixTokensCount */
+        ,
+        1 /* postfixTokensCount */
+        ,
+        ContextFeature::BRACE /* features */
+        ,
+        1 /* contextForbiddenCount */
+        ,
+        0 /* contextSpecForbiddenCount */
+    },
+    ContextDescriptor{
+        6 /* id */
+        ,
+        "(|((a=" /* prefix */
+        ,
+        ")))" /* postfix */
+        ,
+        6 /* prefixTokensCount */
+        ,
+        3 /* postfixTokensCount */
+        ,
+        ContextFeature::BRACE | ContextFeature::DBRACE /* features */
+        ,
+        4 /* contextForbiddenCount */
+        ,
+        0 /* contextSpecForbiddenCount */
+    }};
+
+constexpr static std::array QUOTE_CONTEXTS = {
+    ContextDescriptor{
+        7 /* id */
+        ,
+        "(a=b=\"" /* prefix */
+        ,
+        ")" /* postfix */
+        ,
+        4 /* prefixTokensCount */
+        ,
+        1 /* postfixTokensCount */
+        ,
+        ContextFeature::DQUOTE | ContextFeature::BRACE /* features */
+        ,
+        1 /* contextForbiddenCount */
+        ,
+        0 /* contextSpecForbiddenCount */
+    },
+    ContextDescriptor{
+        8 /* id */
+        ,
+        "(a=b=\"" /* prefix */
+        ,
+        "\")" /* postfix */
+        ,
+        4 /* prefixTokensCount */
+        ,
+        1 /* postfixTokensCount */
+        ,
+        ContextFeature::DQUOTE | ContextFeature::BRACE /* features */
+        ,
+        1 /* contextForbiddenCount */
+        ,
+        0 /* contextSpecForbiddenCount */
+    }};
+
+static ContextFeature get_vector_features(std::string_view vector)
+{
+    size_t braces_count;
+    auto check_feature = [&braces_count](char current_char) {
+        return check_context_feature(current_char, braces_count);
+    };
+
+    using namespace detectos_common::simd;
+    return get_vector_features<ContextFeature>(vector, check_feature, simd_bitmap);
+}
+
+bool DetectDriver::is_injection(std::string_view vector)
+{
+    vector = trim_spaces_left(vector);
+    if (vector.empty()) {
+        return false;
+    }
+    auto features = get_vector_features(vector);
+
+    DEBUG_LOG(std::format("Check vector <--{}--> with features = {}", vector, (int)features));
+
+    bool hasInjection = check_contexts(vector, features, BASE_CONTEXTS);
+    if (!hasInjection && static_cast<int>(features & ContextFeature::DQUOTE)) {
+        hasInjection = check_contexts(vector, features, QUOTE_CONTEXTS);
+    }
+    return hasInjection;
+}
+
+bool DetectDriver::check_contexts(std::string_view vector, ContextFeature vectorFeatures,
+                                  const std::span<const ContextDescriptor> contexts)
+{
+    for (auto context : contexts) {
+        /* Filter context base on vector's features */
+        DEBUG_LOG(std::format("Context with id {}", context.id));
+
+        if ((context.features & vectorFeatures) != context.features) {
+            DEBUG_LOG(std::format("Context with id {} - features not match", context.id));
+            continue;
+        }
+        // Для борьбы с аллокациями на трафике, будем все копировать
+        // в vector_in_context_
+        vector_in_context_ = context.prefix;
+        vector_in_context_.append(vector);
+        vector_in_context_.append(context.postfix);
+
+        if (!is_parsed(vector_in_context_, &context)) {
+            DEBUG_LOG("Vector not parsed with this context");
+            continue;
+        }
+
+        if (forbiddenNodeCount_ > context.contextForbiddenCount ||
+            specForbiddenNodeCount_ > context.contextSpecForbiddenCount) {
+            DEBUG_LOG("Injection found!");
+            return true; /* INJECTION */
+        }
+    }
+
+    DEBUG_LOG("Injection not found: vector is CLEAR");
+    return false /* Injection not found */;
+}
+
+bool DetectDriver::is_parsed(std::string_view vector, ContextDescriptor *context_description)
+{
+    reflex::Input in_vector(vector.data(), vector.size());
+    lexer_.reInit(in_vector, context_description);
+    // Парсер возвращает 0 в случае удачи
+    bool parsed = (parser_.parse() == 0);
+
+    tokensCount_ = lexer_.state().tokensCnt_;
+    forbiddenNodeCount_ = lexer_.state().forbiddenNodeCnt_;
+    specForbiddenNodeCount_ = lexer_.state().specForbiddenNodeCnt_;
+    return parsed;
+}
+} /* namespace ptaf::grammar::ldap */
diff --git a/src/DetectDriver.hh b/src/detect_driver.hh
similarity index 84%
rename from src/DetectDriver.hh
rename to src/detect_driver.hh
index cc67a9e..f185921 100644
--- a/src/DetectDriver.hh
+++ b/src/detect_driver.hh
@@ -47,9 +47,9 @@ THE SOFTWARE.
  */
 #pragma once
 #include <string>
-#include "LdapCommon.hh"
-#include "LdapLexer.hh"
-#include "LdapParser.hh"
+#include "ldap_common.hh"
+#include "ldap_lexer.hh"
+#include "ldap_parser.hh"

 namespace ptaf::grammar::ldap {

@@ -61,18 +61,14 @@ class DetectDriver {
     /*!
      * Основной конструктор. Передаётся готовый лексер
      */
-    DetectDriver(ptaf::grammar::LdapLexer* lex);
-    /*!
-     * Возвращает текущую версию реализации метода обнаружения инъекций по контекстам
-     */
-    std::string version();
+    DetectDriver() = default;
     /*!
      * Проверяет входящий вектор на предмет LDAP-инъекции
      *
      * \param[in] vector Вектор для обнаружения инъекций
      * \return Возвращает 1, если инъекция обнаружена, 0 - иначе
      */
-    bool isInjection(std::string &vector);
+    bool is_injection(std::string_view vector);
     /*!
      * Проверяет входящий вектор на соответствие LDAP-грамматики (search-filter)
      * Метод проверяет корректность входной строки по грамматике ldap, реализованной в
@@ -82,20 +78,27 @@ class DetectDriver {
      * \return Возвращает 1 если входная строка(вектор) является корректным ldap-выражением
      *          0 - иначе
      */
-    bool isParsed(reflex::Input &vector, ptaf::grammar::ldap::ContextDescriptor * ctxDescr);
+    bool is_parsed(std::string_view vector,
+                   ptaf::grammar::ldap::ContextDescriptor *context_description);
     /*!
      * Возвращает количество токенов последнего вектора, парсинг которого осуществлялся

      * \return Количество токенов в последнем распарсенном векторе
      */
-    int lastparseTokensCount() {return this->tokensCount_;}
+    [[nodiscard]] size_t last_parse_tokens_count() const noexcept
+    {
+        return tokensCount_;
+    }
     /*!
-     * Возвращает количество запрещённых, с точки зрения ldap-инъекций, конструкций в
+     * Возвращает количество запрещённых, с точки зрения ldap-инъекций, конструкций в
      *  последнем векторе, парсинг которого осуществлялся
      *
      * \return Количество запрещённых конструкций с точки зрения внедрения инъекций
      */
-    int lastparseForbiddenCount() {return this->forbiddenNodeCount_;}
+    [[nodiscard]] size_t last_parse_forbidden_count() const noexcept
+    {
+        return forbiddenNodeCount_;
+    }
     /*!
      * Возвращает количество запрещённых специальных (требующий более тонкой настройки),
      * с точки зрения ldap-инъекций, конструкций в последнем векторе, парсинг
@@ -103,31 +106,32 @@ class DetectDriver {
      *
      * \return Количество запрещённых специальных конструкций с точки зрения внедрения инъекций
      */
-    int lastparseSpecForbiddenCount() {return this->specForbiddenNodeCount_;}
+    [[nodiscard]] size_t last_parse_spec_forbidden_count() const noexcept
+    {
+        return specForbiddenNodeCount_;
+    }

   private:
+    std::string vector_in_context_;
     /*!
      * Лексер для токенизации входного потока
      */
-    ptaf::grammar::LdapLexer *lexer_;
+    LdapLexer lexer_;
     /*!
      * Парсер для разбора входной строки после токенизации лексером
      */
-    ptaf::grammar::ldap::parser parser_;
+    parser parser_ = &lexer_;
     /*!
      * Осуществляет проверку на инъекции по методу контекстов
      *
      * \template_param[in] N Размер массива структур-контекстов
      * \param[in] vector Вектор для обнаружения инъекции
-     * \param[in] vectorFeatures  Признаки вектора для фильтрации контекстов по которым необходимо вести поиск
-     * \param[in] ctxs Набор контекстов для поиска по ним инъекций
-     * \return Возвращает 1, если по какому-либо контексту обнаружена инъекция
-     *          0 - иначе
+     * \param[in] vectorFeatures  Признаки вектора для фильтрации контекстов по которым необходимо
+     * вести поиск \param[in] ctxs Набор контекстов для поиска по ним инъекций \return Возвращает 1,
+     * если по какому-либо контексту обнаружена инъекция 0 - иначе
      */
-    template <size_t N>
-    bool checkContexts(
-        std::string &vector, int vectorFeatures, const struct ptaf::grammar::ldap::ContextDescriptor (&ctxs)[N]
-    );
+    bool check_contexts(std::string_view vector, ContextFeature vectorFeatures,
+                        std::span<const ContextDescriptor> contexts);
     /*!
      * Количество токенов предыдущего вектора, парсинг которого осуществлялся
      */
@@ -143,4 +147,4 @@ class DetectDriver {
     int specForbiddenNodeCount_ = 0;
 };

-} /* namespace ptaf */
+}  // namespace ptaf::grammar::ldap
diff --git a/src/LdapCommon.hh b/src/ldap_common.hh
similarity index 87%
rename from src/LdapCommon.hh
rename to src/ldap_common.hh
index 5c25793..044fcf6 100644
--- a/src/LdapCommon.hh
+++ b/src/ldap_common.hh
@@ -39,7 +39,7 @@ namespace ptaf::grammar::ldap {
  * Таким образом входной вектор будет проверяться по контексту в том и только
  * в том случае если их характеристики полностью совпадают
  */
-enum ContextFeature {
+enum class ContextFeature {
     /*!
      * Заглушка, обозначающая отсутствие признаков
      */
@@ -56,29 +56,47 @@ enum ContextFeature {
      * Присутствует не менее двух закрывающих круглых скобок
      */
     DBRACE = 0x04,
+    ALL_FLAGS = NONE | DQUOTE | BRACE | DBRACE
 };

+constexpr auto operator&(ContextFeature lhs, ContextFeature rhs) noexcept
+{
+    return static_cast<ContextFeature>(static_cast<int>(lhs) & static_cast<int>(rhs));
+}
+
+constexpr auto operator|(ContextFeature lhs, ContextFeature rhs) noexcept
+{
+    return static_cast<ContextFeature>(static_cast<int>(lhs) | static_cast<int>(rhs));
+}
+
+constexpr auto operator|=(ContextFeature &lhs, ContextFeature rhs) noexcept
+{
+    lhs = lhs | rhs;
+
+    return lhs;
+}
+
 /*!
  * \struct
  * \brief Структура - дескриптор контекста
- *
+ *
  */
 struct ContextDescriptor {
     /* Идентификатор контекста */
-    int id;
+    int id = 0;
     /* Префикс контекста */
     std::string prefix;
     /* Постфикс контекста */
     std::string postfix;
     /* Количество токенов из которых состоит префикс */
-    int prefixTokensCount;
+    int prefixTokensCount = 0;
     /* Количество токенов из которых состоит постфикс */
-    int postfixTokensCount;
+    int postfixTokensCount = 0;
     /*
      * Признаки контекстов.
      * Набор флагов из ptaf::grammar::ldap::ContextFeature
      */
-    int features;
+    ContextFeature features = ContextFeature::NONE;
     /*
      * Количество запрещённых конструкций при парсинге за счёт контекста.
      * Идея в том, что во входных векторах не должно быть запрещённых конструкций,
@@ -87,14 +105,14 @@ struct ContextDescriptor {
      * заранее известным фиксированным значением и других запрещённых конструкций
      * во входном векторе быть не должно, а если есть, то считаем его инъекцией.
      */
-    int contextForbiddenCount;
+    int contextForbiddenCount = 0;
     /*
      * Количество специальных запрещённых конструкций при парсинге за счёт контекста.
      * Логика та же что и для запрещённых конструкций. Но специальные конструкции
      * выявляются сложнее (за счёт комбинации условий) и поэтому выделяются в отдельную
      * категорию
      */
-    int contextSpecForbiddenCount;
+    int contextSpecForbiddenCount = 0;
 };
 /**
  * For now this delta using in 2 cases:
@@ -104,7 +122,7 @@ struct ContextDescriptor {
  *    then it is highly likely ldap-injection
  *  2) Special cases. But such as exists 1) using  for ALLOWED_..._DELTA
  *   then for special DANGER construct it is necessary increment
- *   this->spec_forbidden_counter_ by this DELTA
+ *   spec_forbidden_counter_ by this DELTA
  */
 const int ALLOWED_SPEC_FORBIDDEN_DELTA = 1;
 } /* namespace ptaf::grammar::ldap */
diff --git a/src/ldap_lexer_macros.hh b/src/ldap_lexer_macros.hh
new file mode 100644
index 0000000..e08a1d7
--- /dev/null
+++ b/src/ldap_lexer_macros.hh
@@ -0,0 +1,34 @@
+#pragma once
+
+#define RE_YY_INC_FORBIDDEN_NODE state_.forbiddenNodeCnt_++;
+#define RE_YY_INC_SPEC_FORBIDDEN_NODE state_.specForbiddenNodeCnt_++;
+#define RE_YY_RETURN(tok) return tok;
+#ifdef DEBUG
+#define RE_YY_DEBUG_OUTPUT std::cout << str() << std::endl;
+#else
+#define RE_YY_DEBUG_OUTPUT
+#endif
+#define RE_YY_USER_ACTION \
+    RE_YY_DEBUG_OUTPUT    \
+    state_.tokensCnt_++;
+#define RE_YY_BUFFERED_CNTTOK_AND_RETURN(tok) \
+    RE_YY_DEBUG_OUTPUT                        \
+    state_.bufferedCntTokInDN_++;             \
+    RE_YY_RETURN(tok);
+#define RE_YY_CLEAR_BUFFERED_DN     \
+    state_.bufferedCntTokInDN_ = 0; \
+    state_.bufferedRdnCnt_ = 0;
+#define RE_YY_APPLY_BUFFERED_DN                                                      \
+    if (state_.bufferedRdnCnt_ > 1) {                                                \
+        state_.existsDangerNullByteTokens_ = 1;                                      \
+        if (static_cast<int>(state_.ctxDescr_->features & ContextFeature::DQUOTE)) { \
+            RE_YY_INC_SPEC_FORBIDDEN_NODE                                            \
+        }                                                                            \
+    }                                                                                \
+    state_.tokensCnt_ += state_.bufferedCntTokInDN_;
+#define RE_YY_USER_ACTION_AND_RETURN(tok) \
+    RE_YY_USER_ACTION                     \
+    RE_YY_RETURN(tok)
+#define RE_YY_UNPUT_READED_SYMBOL \
+    char curChar = chr();         \
+    matcher().unput(curChar);
diff --git a/src/ldap_lexer_state.cc b/src/ldap_lexer_state.cc
new file mode 100644
index 0000000..0807c72
--- /dev/null
+++ b/src/ldap_lexer_state.cc
@@ -0,0 +1,50 @@
+#include "ldap_lexer_state.hh"
+
+namespace ptaf::grammar::ldap {
+
+constexpr std::string_view token_type_str(LdapToken token)
+{
+    static constexpr std::array tokens = {"T_UNKNOWN",
+                                          "T_DN_RDN",
+                                          "T_DN_DN_COMMA_RDN",
+                                          "P_LBRACE",
+                                          "P_RBRACE",
+                                          "P_BANG",
+                                          "P_AND",
+                                          "P_PIPE",
+                                          "P_AEQ",
+                                          "P_GE",
+                                          "P_LE",
+                                          "P_COLONEQ",
+                                          "P_ASTERISK",
+                                          "P_EQ",
+                                          "P_COMMA",
+                                          "P_PLUS",
+                                          "T_DN_FLAG",
+                                          "T_MATCHINGRULE",
+                                          "T_ATTR_DESC",
+                                          "T_ATTRTYPE_EQ",
+                                          "T_ASSERT_VALUE",
+                                          "T_BROKEN_DNVALUE",
+                                          "T_END"};
+
+    // сгенерированные бизоном токены идут по порядку начиная с T_UNKNOWN
+    constexpr size_t begin = LdapToken::T_UNKNOWN;
+    return begin + token < tokens.size() ? tokens[token] : "Wrong Token's type";
+}
+
+LexerState::LexerState()
+{
+    clear();
+}
+
+void LexerState::clear()
+{
+    existsDangerNullByteTokens_ = 0;
+    tokensCnt_ = 0;
+    forbiddenNodeCnt_ = 0;
+    specForbiddenNodeCnt_ = 0;
+    bufferedRdnCnt_ = 0;
+    bufferedCntTokInDN_ = 0;
+}
+}  // namespace ptaf::grammar::ldap
diff --git a/src/ldap_lexer_state.hh b/src/ldap_lexer_state.hh
new file mode 100644
index 0000000..3d96a9a
--- /dev/null
+++ b/src/ldap_lexer_state.hh
@@ -0,0 +1,51 @@
+#pragma once
+
+#include <vector>
+#include "ldap_common.hh"
+#include "ldap_parser.hh"
+
+namespace ptaf::grammar::ldap {
+using LdapToken = parser::token_type;
+
+/*
+ * Функция нужна для простоты отладки грамматики.
+ * Используется в парном репозитории с грамматиками, но не в самом детекторе
+ */
+constexpr std::string_view token_type_str(LdapToken token);
+
+class LexerState {
+  public:
+    LexerState();
+    void clear();
+    /*
+     * External DATA with context's descriptor for input vector.
+     * If vector is created from context, then descriptor of this
+     * context must be available. If not - values in descriptor
+     * don't matter
+     */
+    ContextDescriptor *ctxDescr_ = nullptr;
+    /*
+     * Some null-byte injection close to false-positives. In order
+     * to distinct this cases use additional marker for dangers
+     * tokens for null-byte injection
+     */
+    bool existsDangerNullByteTokens_ = 0;
+    /*
+     * Count of Tokens in input vector
+     * Used for Context Detection Algorithm
+     */
+    size_t tokensCnt_ = 0;
+
+    /*
+     * Check if input vector consist forbidden construct in AST
+     */
+    size_t forbiddenNodeCnt_ = 0;
+    size_t specForbiddenNodeCnt_ = 0;
+    /*
+     * Buffered count of RDN-element in DN. If DN real, not broken, then
+     *  it is necessary use this buffered count
+     */
+    size_t bufferedRdnCnt_ = 0;
+    size_t bufferedCntTokInDN_ = 0;
+};
+}  // namespace ptaf::grammar::ldap
diff --git a/src/ldapi_detector.cc b/src/ldapi_detector.cc
index 510a706..930debf 100644
--- a/src/ldapi_detector.cc
+++ b/src/ldapi_detector.cc
@@ -1,83 +1,39 @@
-#include <lua.hpp>
+#include "ldapi_detector.hh"
+#include "detect_driver.hh"
+#include "ldap_common.hh"
+
 #include <string>
-#include "LdapCommon.hh"
-#include "DetectDriver.hh"

 namespace ptaf::grammar::ldap {
-    static ptaf::grammar::ldap::ContextDescriptor defaultContextDescriptor = {
-        0 /* id */
-        , "" /* prefix */
-        , "" /* postfix */
-        , 0 /* prefixTokensCount */
-        , 0 /* postfixTokensCount */
-        , ptaf::grammar::ldap::ContextFeature::NONE /* features */
-        , 0 /* contextForbiddenCount */
-        , 0 /* contextSpecForbiddenCount */
-    };
-    static ptaf::grammar::LdapLexer ldapLexer(&defaultContextDescriptor, std::string("ldap init"));
-    static ptaf::grammar::ldap::DetectDriver ldapDetectorDriver(&ldapLexer);
+LdapiDetector::LdapiDetector() : impl_(std::make_unique<ptaf::grammar::ldap::DetectDriver>())
+{
+}
+
+LdapiDetector::~LdapiDetector() = default;
+
+bool LdapiDetector::isInjection(std::string_view data) const
+{
+    return impl_->is_injection(data);
 }

-extern "C" int hasLdapiAttack(lua_State *L)
+bool LdapiDetector::isParsed(std::string_view data) const
 {
-    const int VECTOR_ARG_IDX = 1;
-    const char *s;
-    size_t realStringLength;
-    /* Skip unused args */
-    if(lua_gettop(L) > VECTOR_ARG_IDX) {
-        lua_pop(L, lua_gettop(L) - VECTOR_ARG_IDX);
-    }
-    /* Check if first arg exists and this is string */
-    //TODO: throw error if input is not string
-    if(
-        lua_gettop(L) == VECTOR_ARG_IDX &&
-        lua_type(L, VECTOR_ARG_IDX) == LUA_TSTRING
-    ) {
-        /* Check alone input string for injection */
-        s = luaL_checklstring(L, VECTOR_ARG_IDX, &realStringLength);
-        std::string vector(s, realStringLength);
-        lua_pushboolean(L, ptaf::grammar::ldap::ldapDetectorDriver.isInjection(vector));
-        return 1;
-    }
-    /* If there is no arg return false */
-    lua_pushboolean(L, 0);
-    return 1;
+    ptaf::grammar::ldap::ContextDescriptor ctx_descriptor;
+    return impl_->is_parsed(data, &ctx_descriptor);
 }

-extern "C" int isLdapParsed(lua_State *L)
+size_t LdapiDetector::lastparseTokensCount() const
 {
-    size_t realStringLength;
-    const char *s = luaL_checklstring(L, 1, &realStringLength);
-    reflex::Input inVector(s, realStringLength);
-    lua_pushboolean(
-        L, ptaf::grammar::ldap::ldapDetectorDriver.isParsed(
-            inVector, &ptaf::grammar::ldap::defaultContextDescriptor
-        )
-    );
-    lua_pushboolean(L,
-            ptaf::grammar::ldap::ldapDetectorDriver.lastparseForbiddenCount()
-            - ptaf::grammar::ldap::defaultContextDescriptor.contextForbiddenCount > 0
-        or
-            ptaf::grammar::ldap::ldapDetectorDriver.lastparseSpecForbiddenCount()
-            - ptaf::grammar::ldap::defaultContextDescriptor.contextSpecForbiddenCount > 0
-    );
-    return 2;
+    return impl_->last_parse_tokens_count();
 }

-extern "C" int version(lua_State *L)
+size_t LdapiDetector::lastparseForbiddenCount() const
 {
-    lua_pushstring(L, ptaf::grammar::ldap::ldapDetectorDriver.version().c_str());
-    return 1;
+    return impl_->last_parse_forbidden_count();
 }

-extern "C" int luaopen_ldapi_detector(lua_State *L)
+size_t LdapiDetector::lastparseSpecForbiddenCount() const
 {
-    static const struct luaL_Reg cfuncForLua [] = {
-        {"has_attack", hasLdapiAttack},
-        {"is_parsed", isLdapParsed},
-        {"version", version},
-        {NULL, NULL} /* sentinel */
-    };
-    luaL_register(L, "ldapi_detector", cfuncForLua);
-    return 1;
+    return impl_->last_parse_spec_forbidden_count();
 }
+}  // namespace ptaf::grammar::ldap
diff --git a/src/ldapi_detector.hh b/src/ldapi_detector.hh
new file mode 100644
index 0000000..bfd61ec
--- /dev/null
+++ b/src/ldapi_detector.hh
@@ -0,0 +1,59 @@
+#pragma once
+
+#include <memory>
+#include <string_view>
+
+namespace ptaf::grammar::ldap {
+class DetectDriver;
+/**
+ * @class LdapiDetector
+ * @brief Детектор атак LDAP-инъекции
+ * @see https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html
+ * для более подробной информации об атаке LDAP-инъекции
+ */
+class LdapiDetector {
+  public:
+    LdapiDetector();
+    ~LdapiDetector();
+
+    /**
+     * @brief Проверяет наличие атаки LDAP-инъекции
+     * @param data Входные данные
+     * @return True, если атака обнаружена, false иначе
+     */
+    bool isInjection(std::string_view data) const;  // Код стайл сохранен для совместимости с ядром
+
+    /**
+     * @brief Проверяет возможность парсинга входных данных
+     * @param data Входные данные
+     * @return True, если парсинг успешен, false иначе
+     */
+    bool isParsed(std::string_view data) const;  // Код стайл сохранен для совместимости с ядром
+
+    /**
+     * @brief Возвращает количество токенов, обнаруженных при последнем парсинге
+     * @return Количество токенов
+     */
+    size_t lastparseTokensCount() const;  // Код стайл сохранен для совместимости с ядром
+
+    /**
+     * @brief Возвращает количество запрещенных токенов, обнаруженных при последнем парсинге
+     * @return Количество запрещенных токенов
+     */
+    size_t lastparseForbiddenCount() const;  // Код стайл сохранен для совместимости с ядром
+
+    /**
+     * @brief Возвращает количество специальных запрещенных токенов, обнаруженных при последнем
+     * парсинге
+     * @return Количество специальных запрещенных токенов
+     */
+    size_t lastparseSpecForbiddenCount() const;  // Код стайл сохранен для совместимости с ядром
+
+  private:
+    /*
+     *  PIMPL используется, чтобы избежать поставки сгенерированных
+     *  хидеров вместе с библиотекой.
+     */
+    std::unique_ptr<ptaf::grammar::ldap::DetectDriver> impl_;
+};
+}  // namespace ptaf::grammar::ldap
diff --git a/src/ldapi_detector_ffi.cc b/src/ldapi_detector_ffi.cc
new file mode 100644
index 0000000..6294cbe
--- /dev/null
+++ b/src/ldapi_detector_ffi.cc
@@ -0,0 +1,111 @@
+#include "detectors-api/api.hh"
+#include "ldapi_detector.hh"
+/**
+ * @defgroup LDAP Injection Детектор
+ * @{
+ * @see https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html
+ */
+
+namespace {
+using ptaf::grammar::ldap::LdapiDetector;
+constexpr version_t api_version = {
+    .major = API_VERSION_MAJOR, .minor = API_VERSION_MINOR, .patch = API_VERSION_PATCH};
+constexpr version_t detector_version = {
+    .major = VERSION_MAJOR, .minor = VERSION_MINOR, .patch = VERSION_PATCH};
+
+/**
+ * @brief Проверяет наличие атаки
+ * @param self Указатель на структуру API детектора
+ * @param input Входные данные
+ * @param length Длина входных данных
+ * @return true, если атака обнаружена, false иначе
+ */
+bool has_attack(detector_api_ptr self, const char *input, size_t length)
+{
+    return static_cast<LdapiDetector *>(self->detector)
+        ->isInjection(std::string_view{input, length});
+}
+
+/**
+ * @brief Проверяет возможность парсинга
+ * @param self Указатель на структуру API детектора
+ * @param input Входные данные
+ * @param length Длина входных данных
+ * @return true, если парсинг успешен, false иначе
+ */
+bool is_parsed(detector_api_ptr self, const char *input, size_t length)
+{
+    return static_cast<LdapiDetector *>(self->detector)->isParsed(std::string_view{input, length});
+}
+
+/**
+ * @brief Возвращает количество токенов, обнаруженных при последнем парсинге
+ *
+ * @param detector_api_ptr Указатель на экземпляр API детектора
+ * @return Количество токенов
+ */
+uint16_t last_parse_tokens_count(detector_api_ptr self)
+{
+    return static_cast<LdapiDetector *>(self->detector)->lastparseTokensCount();
+}
+
+/**
+ * @brief Возвращает количество запрещенных токенов, обнаруженных при последнем парсинге
+ *
+ * @param detector_api_ptr Указатель на экземпляр API детектора
+ * @return Количество запрещенных токенов
+ */
+uint16_t last_parse_forbidden_count(detector_api_ptr self)
+{
+    return static_cast<LdapiDetector *>(self->detector)->lastparseForbiddenCount();
+}
+
+/**
+ * @brief Возвращает количество специальных запрещенных токенов, обнаруженных при последнем парсинге
+ *
+ * @param detector_api_ptr Указатель на экземпляр API детектора
+ * @return Количество специальных запрещенных токенов
+ */
+uint16_t last_parse_spec_forbidden_count(detector_api_ptr self)
+{
+    return static_cast<LdapiDetector *>(self->detector)->lastparseSpecForbiddenCount();
+}
+
+}  // namespace
+
+/**
+ * @brief Уничтожает экземпляр детектора
+ * @param self Указатель на структуру API детектора
+ */
+void detector_destroy(detector_api_ptr self)
+{
+    if (!self) {
+        return;
+    }
+    if (self->detector) {
+        delete static_cast<LdapiDetector *>(self->detector);
+    }
+    delete self;
+}
+
+/**
+ * @brief Создает экземпляр API детектора
+ * @return Указатель на структуру API детектора
+ */
+detector_api_ptr detector_create()
+{
+    auto instance = new detector_api_t;
+    instance->detector = new LdapiDetector;
+    instance->api_version = api_version;
+    instance->detector_version = detector_version;
+    instance->ci_build_number = CI_BUILD_NUMBER;
+    instance->destroy = detector_destroy;
+    instance->has_attack = has_attack;
+    instance->is_parsed = is_parsed;
+    instance->last_parse_tokens_count = last_parse_tokens_count;
+    instance->last_parse_forbidden_count = last_parse_forbidden_count;
+    instance->last_parse_spec_forbidden_count = last_parse_spec_forbidden_count;
+    return instance;
+}
+
+/** @} */
diff --git a/src/profiled_test.cc b/src/profiled_test.cc
index 576e059..7fde6bf 100644
--- a/src/profiled_test.cc
+++ b/src/profiled_test.cc
@@ -1,59 +1,75 @@
 #include <iostream>

-#include "LdapCommon.hh"
 #include "DetectDriver.hh"
+#include "LdapCommon.hh"

 namespace ptaf::grammar::ldap {
-    static ptaf::grammar::ldap::ContextDescriptor defaultContextDescriptor = {
-        0 /* id */
-        , "" /* prefix */
-        , "" /* postfix */
-        , 0 /* prefixTokensCount */
-        , 0 /* postfixTokensCount */
-        , ptaf::grammar::ldap::ContextFeature::NONE /* features */
-        , 0 /* contextForbiddenCount */
-        , 0 /* contextSpecForbiddenCount */
-    };
-    static ptaf::grammar::LdapLexer ldapLexer(&defaultContextDescriptor, std::string("ldap init"));
-    static ptaf::grammar::ldap::DetectDriver ldapDetectorDriver(&ldapLexer);
-}
-
+static ptaf::grammar::ldap::ContextDescriptor defaultContextDescriptor = {
+    0 /* id */
+    ,
+    "" /* prefix */
+    ,
+    "" /* postfix */
+    ,
+    0 /* prefixTokensCount */
+    ,
+    0 /* postfixTokensCount */
+    ,
+    ptaf::grammar::ldap::ContextFeature::NONE /* features */
+    ,
+    0 /* contextForbiddenCount */
+    ,
+    0 /* contextSpecForbiddenCount */
+};
+static ptaf::grammar::LdapLexer ldapLexer(&defaultContextDescriptor, std::string("ldap init"));
+static ptaf::grammar::ldap::DetectDriver ldapDetectorDriver(&ldapLexer);
+}  // namespace ptaf::grammar::ldap

 int main()
 {
     const int experimentsCount = 1e6;
     int i = 0;
     std::string vectorList[] = {
-        std::string("Test\\FF,OU=Admins,DC=testlab,DC=local)\x00", (size_t)39)
-        , std::string("b")
-        , std::string("\x20\x00\x00\x00")
-        , std::string("Vm\x00\x82\xB9\xFD\xEA\xD3\xF5.\xA5""f\x97\x9D\x94\x0A")
-        , std::string("PHPSESSID=dnjcpjq3qv84lpegut5o20g8h1&action=dlattach;attach=38;type=avatar")
-        , std::string("PHPSESSID=fb7a47a88fb406afe8d152597afb8e71;thememode=mobile;redirect=http\x3A\x2F\x2F""forum.dizelist.ru\x2Findex.php\x3Ftopic\x3D""3016.0")
-        , std::string("act=Profile;CODE=03;MID=68-1463482044")
-        , std::string("*)(sn=*")
-        , std::string("+7(999)888-77-66")
-        , std::string("36197")
-        , std::string("aa=111; httponly; secure")
-        , std::string("aa=bb=111;")
-        , std::string("0sjoqmlb2jccj&b=3&s=65")
-        , std::string("${RS}|OTu77jk4LjEOTxq1VimxkxcbODIuMlZ44eIAAAAA|2023538075|TL1|1450762722.851765|2-9-1:ysd:1")
-        , std::string("(136t3lvk1(gid$OTu77jk4LjEOTxq1VimxkxcbODIuMlZ44eIAAAAA,st$1450762722062674,si$4452051,sp$2023538075,pv$1,v$2.0))")
-        , std::string("/l_t@/_Feu1wvhtpass2/1nieQnnrvnzktuasain/tg1ARIfG_oNC_d/ms/o1xRytTk34/oVkR_D8Zz/dWVCNK7AQ-m1CRGy_/zYHrk2P0brDP/oe/pYYxRGgNhIk2N1tWiI.png?crTeYreti=wsn&et3tf6shoV=tdsviee y fum\x24oh3\x3Bore&sAib5hfAvhEpC=tcilbrr Lne")
-        , std::string("eb9adbd87d) (userAccountControl:1.2.840.113556.1.4.803:=65536")
-        , std::string("Basic TnJ3MDY6UWVzc29sY2U=")
-        , std::string("oarraatavd=tisrP3n5mopsy;C.psdnB=87378")
-        , std::string("Test\x2BOU =Admins, DC =testlab, DC =local)\x00", (size_t)41)
-        , std::string("/suGdrVj.cfm?seivste3c=804252514&Gxnc1atstirc3eR=eA&ioe9ogl=\x3B\x7E&J7etc88Op=7\x24gr stx&HWlTW=c2.2mwQ&anE5=TAistyle&usi=la &md=dNt\x40&zs=\x5Dt\x7ChmEh")
-        , std::string("FTP/9.5 www.lEiieigy.jpg:2, HTTP/1.8 www.ie3anshn.css, 6.2 240.233.126.158:4")
-        , std::string("/ez/FQY/9WcO64.dll?n7soevann9r=ef9UgkzcZ&Nirldiea=bgbody30")
-        , std::string("oarraatavd=tisrP3n5mopsy;C.psdnB=87378")
-        , std::string("example.com\",OU=Secret,DC=testlab,DC=\"zzzz\\\"zzz)\x00", (size_t)49)
-        , std::string("deflate,gzip,gzip;q=0.7")
-        , std::string("oenGtle0=8588;enlaapbsdsAJeet=auigutd;nRyo1Jctelnetx56Y=adt")
-    };
-    while(i < experimentsCount) {
-        for(auto vector: vectorList) {
+        std::string("Test\\FF,OU=Admins,DC=testlab,DC=local)\x00", (size_t)39),
+        std::string("b"),
+        std::string("\x20\x00\x00\x00"),
+        std::string("Vm\x00\x82\xB9\xFD\xEA\xD3\xF5.\xA5"
+                    "f\x97\x9D\x94\x0A"),
+        std::string("PHPSESSID=dnjcpjq3qv84lpegut5o20g8h1&action=dlattach;attach=38;type=avatar"),
+        std::string(
+            "PHPSESSID=fb7a47a88fb406afe8d152597afb8e71;thememode=mobile;redirect=http\x3A\x2F\x2F"
+            "forum.dizelist.ru\x2Findex.php\x3Ftopic\x3D"
+            "3016.0"),
+        std::string("act=Profile;CODE=03;MID=68-1463482044"),
+        std::string("*)(sn=*"),
+        std::string("+7(999)888-77-66"),
+        std::string("36197"),
+        std::string("aa=111; httponly; secure"),
+        std::string("aa=bb=111;"),
+        std::string("0sjoqmlb2jccj&b=3&s=65"),
+        std::string("${RS}|OTu77jk4LjEOTxq1VimxkxcbODIuMlZ44eIAAAAA|2023538075|TL1|1450762722."
+                    "851765|2-9-1:ysd:1"),
+        std::string("(136t3lvk1(gid$OTu77jk4LjEOTxq1VimxkxcbODIuMlZ44eIAAAAA,st$1450762722062674,"
+                    "si$4452051,sp$2023538075,pv$1,v$2.0))"),
+        std::string("/l_t@/_Feu1wvhtpass2/1nieQnnrvnzktuasain/tg1ARIfG_oNC_d/ms/o1xRytTk34/"
+                    "oVkR_D8Zz/dWVCNK7AQ-m1CRGy_/zYHrk2P0brDP/oe/"
+                    "pYYxRGgNhIk2N1tWiI.png?crTeYreti=wsn&et3tf6shoV=tdsviee y "
+                    "fum\x24oh3\x3Bore&sAib5hfAvhEpC=tcilbrr Lne"),
+        std::string("eb9adbd87d) (userAccountControl:1.2.840.113556.1.4.803:=65536"),
+        std::string("Basic TnJ3MDY6UWVzc29sY2U="),
+        std::string("oarraatavd=tisrP3n5mopsy;C.psdnB=87378"),
+        std::string("Test\x2BOU =Admins, DC =testlab, DC =local)\x00", (size_t)41),
+        std::string(
+            "/suGdrVj.cfm?seivste3c=804252514&Gxnc1atstirc3eR=eA&ioe9ogl=\x3B\x7E&J7etc88Op="
+            "7\x24gr stx&HWlTW=c2.2mwQ&anE5=TAistyle&usi=la &md=dNt\x40&zs=\x5Dt\x7ChmEh"),
+        std::string("FTP/9.5 www.lEiieigy.jpg:2, HTTP/1.8 www.ie3anshn.css, 6.2 240.233.126.158:4"),
+        std::string("/ez/FQY/9WcO64.dll?n7soevann9r=ef9UgkzcZ&Nirldiea=bgbody30"),
+        std::string("oarraatavd=tisrP3n5mopsy;C.psdnB=87378"),
+        std::string("example.com\",OU=Secret,DC=testlab,DC=\"zzzz\\\"zzz)\x00", (size_t)49),
+        std::string("deflate,gzip,gzip;q=0.7"),
+        std::string("oenGtle0=8588;enlaapbsdsAJeet=auigutd;nRyo1Jctelnetx56Y=adt")};
+    while (i < experimentsCount) {
+        for (auto vector : vectorList) {
             ptaf::grammar::ldap::ldapDetectorDriver.isInjection(vector);
             ++i;
         }
'''

question = '''
Как С++ разработчик сделай классический code review для изменений в коде.
Для каждого файла:
Изложи кратко что было сделано.
Если есть критические замечания, опиши и предложи вариант исправления.
Обрати внимание на опечатки.
Не упоминай том, что комментарии на русском языке, это норма.
Если что нибудь можно оптимизировать, предложи вариант как.
'''

prompt = str.format("<|begin_of_text|><|start_header_id|>user<|end_header_id|> {} Вот измененя : {}<|eot_id|><|start_header_id|>assistant<|end_header_id|>", question, diff_str)

client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url=base_url
)

completion = client.completions.create(
    temperature=0.7,
    model=model,
    prompt=prompt,
    stream=False,
    max_tokens=1024
)

print(completion.choices[0].text)