/*******************************************************************************

   This file is part of PyTango, a python binding for Tango

   http://www.tango-controls.org/static/PyTango/latest/doc/html/index.html

   Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
   
   PyTango is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   
   PyTango is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.
  
   You should have received a copy of the GNU Lesser General Public License
   along with PyTango.  If not, see <http://www.gnu.org/licenses/>.
   
*******************************************************************************/

#include <boost/python.hpp>
#include <tango.h>

using namespace boost::python;

void export_periodic_event_info()
{
    class_<Tango::PeriodicEventInfo>("PeriodicEventInfo",
        "A structure containing available periodic event information for an attribute\n"
        "with the folowing members,\n"
        " - period : string\n"
        " - extensions : vector of strings\n"
        )
        .def_readwrite("period", &Tango::PeriodicEventInfo::period)
        .def_readwrite("extensions", &Tango::PeriodicEventInfo::extensions)
    ;
}
