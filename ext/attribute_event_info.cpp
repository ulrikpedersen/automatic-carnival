/******************************************************************************
  This file is part of PyTango (http://pytango.rtfd.io)

  Copyright 2006-2012 CELLS / ALBA Synchrotron, Bellaterra, Spain
  Copyright 2013-2014 European Synchrotron Radiation Facility, Grenoble, France

  Distributed under the terms of the GNU Lesser General Public License,
  either version 3 of the License, or (at your option) any later version.
  See LICENSE.txt for more info.
******************************************************************************/

#include "precompiled_header.hpp"
#include <tango/tango.h>

using namespace boost::python;

void export_attribute_event_info()
{
    class_<Tango::AttributeEventInfo>("AttributeEventInfo")
       .enable_pickling()
       .def_readwrite("ch_event", &Tango::AttributeEventInfo::ch_event)
       .def_readwrite("per_event", &Tango::AttributeEventInfo::per_event)
       .def_readwrite("arch_event", &Tango::AttributeEventInfo::arch_event)
    ;
}
