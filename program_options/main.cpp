#include <boost/program_options/options_description.hpp>
#include <boost/program_options/variables_map.hpp>
#include <boost/program_options/option.hpp>
#include <boost/program_options/parsers.hpp>
#include <iostream>

using namespace std;

namespace po = boost::program_options;



int main(int argc, char const *argv[])
{

	cout << " **** Hi ****" << endl;

	po::options_description lineOptions;
	lineOptions.add_options()
                        ("help,h", "print help")
                        ("version,v", "print version string")
                        ("background,b", "start in the background")
                        ("tconfigfile,t",
                po::value<std::string>()->default_value("param param pam"),
                "set path to config file");
    
    po::variables_map     m_vm;

    auto parsed = po::command_line_parser(argc, argv).options(lineOptions).allow_unregistered().run();
                
    if (!parsed.options.empty()) {
        po::store(parsed, m_vm);
        po::notify(m_vm);
    } else {
         std::cout << lineOptions << std::endl;
        return 1;
    }


	std::cout << "#################################################  " << m_vm["tconfigfile"].as< std::string >() << std::endl;
	/* code */
	return 0;
}