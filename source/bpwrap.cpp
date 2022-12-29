#include <string>
#include <boost/python.hpp>

#include "pytango/pytango.hpp"

using namespace boost::python;

BOOST_PYTHON_MODULE(pytango)
{
    class_<exported_class>("ExportedClass")
        .def("addnumbers", &exported_class::addnumbers)
        .def("name", &exported_class::name)
    ;
}
