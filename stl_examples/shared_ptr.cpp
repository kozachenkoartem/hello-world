

#include <iostream>



template<typename T>
class shared_ptr
{
	struct control_block {
		size_t count = 1;
		T *ptr;

		control_block(T *ptr = nullptr):ptr(ptr) {}
		~control_block() {
			delete ptr;
		}
	};

	void decrease_count(){

		if (!m_cb) return;
		if (--m_cb->count == 0) {
			delete m_cb;
		}
	}

	void increase_count() {
		if (!m_cb) throw " error!";
		m_cb->count ++;
	}

public:

	control_block *m_cb = nullptr; 

	shared_ptr() noexcept {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
	};

	shared_ptr(T *ptr) {
		m_cb = new control_block(ptr);
	}

	shared_ptr& operator=(const shared_ptr &other) noexcept {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
		if(other.m_cb) {
			m_cb = other.m_cb;
			increase_count();
		}

		return *this;
	}

	shared_ptr(const shared_ptr &other) noexcept {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
		*this = other;
	}

	shared_ptr& operator=(
		shared_ptr &&other) noexcept {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
		decrease_count();
		if(other.m_cb) {
			m_cb = other.m_cb;
			other.m_cb = nullptr;
		}
		return *this;
	}


	shared_ptr(shared_ptr &&other) noexcept {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
		*this = other;
	}

	~shared_ptr() {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
		decrease_count();
	}
	
};


template<typename T, typename... Args>
shared_ptr<T>make_shared(const Args&... args){
	return shared_ptr<T>(new T(args...));
}

struct A {
	A(int a = 0, int b = 0, int c = 0) {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
	}

	~A() {
		std::cerr << __PRETTY_FUNCTION__ << std::endl;
	}
};

int main()
{

	auto p = make_shared<A>(1, 2, 3);

	shared_ptr<A> p1(new A);
	p1 = new A;
	return 0;
}