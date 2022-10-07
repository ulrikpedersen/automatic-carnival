/******************************************************************************
  This file is part of PyTango (http://pytango.rtfd.io)

  Copyright 2006-2012 CELLS / ALBA Synchrotron, Bellaterra, Spain
  Copyright 2013-2014 European Synchrotron Radiation Facility, Grenoble, France

  Distributed under the terms of the GNU Lesser General Public License,
  either version 3 of the License, or (at your option) any later version.
  See LICENSE.txt for more info.
******************************************************************************/

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"

extern const char *param_must_be_seq;
extern const char *unreachable_code;
extern const char *non_string_seq;

const char *param_numb_or_str_numb = "Second parameter must be an int or a string representing an int";

struct PyDatabase
{
    struct PickleSuite : bopy::pickle_suite
    {
        static bopy::tuple getinitargs(Tango::Database& self)
        {
            std::string& host = self.get_db_host();
            std::string& port = self.get_db_port();
            if (host.size() > 0 && port.size() > 0)
            {
                return bopy::make_tuple(host, port);
            }
            else
                return bopy::make_tuple();
        }
    };

    static inline boost::shared_ptr<Tango::Database>
    makeDatabase_host_port1(const std::string &host, int port)
    {
        AutoPythonAllowThreads guard;
        return boost::shared_ptr<Tango::Database>(new Tango::Database(const_cast<std::string&>(host), port),
                                                  DeleterWithoutGIL());
    }

    static inline boost::shared_ptr<Tango::Database>
    makeDatabase_host_port2(const std::string &host, const std::string &port_str)
    {
        std::istringstream port_stream(port_str);
        int port = 0;
        if(!(port_stream >> port))
        {
            raise_(PyExc_TypeError, param_numb_or_str_numb);
        }
        AutoPythonAllowThreads guard;
        return boost::shared_ptr<Tango::Database>(new Tango::Database(const_cast<std::string&>(host), port),
                                                  DeleterWithoutGIL());
    }

    static inline boost::shared_ptr<Tango::Database>
    makeDatabase_file(const std::string &filename)
    {
        AutoPythonAllowThreads guard;
        return boost::shared_ptr<Tango::Database>(new Tango::Database(const_cast<std::string&>(filename)),
                                                  DeleterWithoutGIL());
    }

    static inline boost::python::str
    get_device_alias(Tango::Database& self, const std::string &alias)
    {
        std::string devname;
        self.get_device_alias(alias, devname);
        return boost::python::str(devname);
    }

    static inline boost::python::str
    get_alias(Tango::Database& self, const std::string &devname)
    {
        std::string alias;
        self.get_alias(devname, alias);
        return boost::python::str(alias);
    }

    static inline void
    get_device_property_list2(Tango::Database& self, const std::string &devname,
                              const std::string &wildcard, StdStringVector &d)
    {
        self.get_device_property_list(const_cast<std::string&>(devname), wildcard, d);
    }

    static inline boost::python::str
    get_attribute_alias(Tango::Database& self, const std::string &alias)
    {
        std::string attrname;
        self.get_attribute_alias(alias, attrname);
        return boost::python::str(attrname);
    }

    static inline void
    export_event(Tango::Database& self, const boost::python::object &obj)
    {
        Tango::DevVarStringArray par;
        convert2array(obj, par);
        self.export_event(&par);
    }

    static inline boost::python::str dev_name(Tango::Database& self)
    {
        Tango::Connection *conn = static_cast<Tango::Connection *>(&self);
        return boost::python::str(conn->dev_name());
    }

    //static inline boost::python::str get_file_name(Tango::Database& self)
    //{
    //    return boost::python::str(self.get_file_name());
    //}

    static inline boost::python::str
    get_device_from_alias(Tango::Database& self, const std::string &input)
    {
        std::string output;
        self.get_device_from_alias(input, output);
        return boost::python::str(output);
    }

    static inline boost::python::str
    get_alias_from_device(Tango::Database& self, const std::string &input)
    {
        std::string output;
        self.get_alias_from_device(input, output);
        return boost::python::str(output);
    }

    static inline boost::python::str
    get_attribute_from_alias(Tango::Database& self, const std::string &input)
    {
        std::string output;
        self.get_attribute_from_alias(input, output);
        return boost::python::str(output);
    }

    static inline boost::python::str
    get_alias_from_attribute(Tango::Database& self, const std::string &input)
    {
        std::string output;
        self.get_alias_from_attribute(input, output);
        return boost::python::str(output);
    }
};

void export_database()
{
    bopy::class_<Tango::Database, bopy::bases<Tango::Connection> > Database("Database", bopy::init<>())
    ;

    Database
        .def(bopy::init<const Tango::Database &>())
        .def("__init__", bopy::make_constructor(PyDatabase::makeDatabase_host_port1))
        .def("__init__", bopy::make_constructor(PyDatabase::makeDatabase_host_port2))
        .def("__init__", bopy::make_constructor(PyDatabase::makeDatabase_file))

        //
        // Pickle
        //
        .def_pickle(PyDatabase::PickleSuite())

        //
        // general methods
        //
        .def("dev_name", &PyDatabase::dev_name)
        .def("write_filedatabase", &Tango::Database::write_filedatabase)
        .def("reread_filedatabase", &Tango::Database::write_filedatabase)
        .def("build_connection", &Tango::Database::write_filedatabase)
        .def("check_tango_host", &Tango::Database::check_tango_host)
        .def("check_access_control", &Tango::Database::check_access_control)
        .def("is_control_access_checked",
            &Tango::Database::is_control_access_checked)
        .def("set_access_checked",
            &Tango::Database::set_access_checked)
        .def("get_access_except_errors",
            &Tango::Database::get_access_except_errors,
            bopy::return_internal_reference<1>())
        .def("is_multi_tango_host", &Tango::Database::is_multi_tango_host)
        .def("get_file_name", &Tango::Database::get_file_name,
            bopy::return_value_policy<bopy::copy_const_reference>())

        //
        // General methods
        //

        .def("get_info",&Tango::Database::get_info)
        .def("get_host_list",
            (Tango::DbDatum (Tango::Database::*) ())
            &Tango::Database::get_host_list)
        .def("get_host_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_host_list)
        .def("get_services",
            (Tango::DbDatum (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_services)
        .def("get_device_service_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_service_list)
        .def("register_service",
            (void (Tango::Database::*) (const std::string &, const std::string &, const std::string &))
            &Tango::Database::register_service)
        .def("unregister_service",
            (void (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::unregister_service)

        //
        // Device methods
        //

        .def("add_device", &Tango::Database::add_device)
        .def("delete_device", &Tango::Database::delete_device)
        .def("import_device",
            (Tango::DbDevImportInfo (Tango::Database::*) (const std::string &))
            &Tango::Database::import_device)
        .def("export_device", &Tango::Database::export_device)
        .def("unexport_device", &Tango::Database::unexport_device)
        .def("get_device_info",
            (Tango::DbDevFullInfo (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_info)
        .def("get_device_name",
            (Tango::DbDatum (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_device_name)
        .def("get_device_exported",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_exported)
        .def("get_device_domain",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_domain)
        .def("get_device_family",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_family)
        .def("get_device_member",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_member)
        .def("get_device_alias", &PyDatabase::get_device_alias)
        .def("get_alias", &PyDatabase::get_alias)
        .def("get_device_alias_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_alias_list)
        .def("get_class_for_device",
            (std::string (Tango::Database::*) (const std::string &))
            &Tango::Database::get_class_for_device)
        .def("get_class_inheritance_for_device",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_class_inheritance_for_device)
        .def("get_device_exported_for_class",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_exported_for_class)
        .def("put_device_alias",
            (void (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::put_device_alias)
        .def("delete_device_alias",
            (void (Tango::Database::*) (const std::string &))
            &Tango::Database::delete_device_alias)

        //
        // server methods
        //

        .def("_add_server",
            (void (Tango::Database::*) (const std::string &, Tango::DbDevInfos &))
            &Tango::Database::add_server)
        .def("delete_server",
            (void (Tango::Database::*) (const std::string &))
            &Tango::Database::delete_server)
        .def("_export_server", &Tango::Database::export_server)
        .def("unexport_server",
            (void (Tango::Database::*) (const std::string &))
            &Tango::Database::unexport_server)
        .def("rename_server", &Tango::Database::rename_server,
            ( arg_("self"), arg_("old_ds_name"), arg_("new_ds_name") ))
        .def("get_server_info",
            (Tango::DbServerInfo (Tango::Database::*) (const std::string &))
            &Tango::Database::get_server_info)
        .def("put_server_info", &Tango::Database::put_server_info,
            ( arg_("self"), arg_("info") ))
        .def("delete_server_info",
            (void (Tango::Database::*) (const std::string &))
            &Tango::Database::delete_server_info)
        .def("get_server_class_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_server_class_list)
        .def("get_server_name_list", &Tango::Database::get_server_name_list)
        .def("get_instance_name_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_instance_name_list)
        .def("get_server_list",
            (Tango::DbDatum (Tango::Database::*) ())
            &Tango::Database::get_server_list)
        .def("get_server_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_server_list)
        .def("get_host_server_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_host_server_list)
        .def("get_device_class_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_device_class_list)
        .def("get_server_release", &Tango::Database::get_server_release)

        //
        // property methods
        //

        .def("_get_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_property)
        .def("_get_property_forced", &Tango::Database::get_property_forced)
        .def("_put_property", &Tango::Database::put_property)
        .def("_delete_property", &Tango::Database::delete_property)
        .def("get_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_property_history)
        .def("get_object_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_object_list)
        .def("get_object_property_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_object_property_list)
        .def("_get_device_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_device_property)
        .def("_put_device_property", &Tango::Database::put_device_property)
        .def("_delete_device_property", &Tango::Database::delete_device_property)
        .def("get_device_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_device_property_history)
        .def("_get_device_property_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_device_property_list)
        .def("_get_device_property_list", &PyDatabase::get_device_property_list2)
        .def("_get_device_attribute_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_device_attribute_property)
        .def("_get_device_pipe_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_device_pipe_property)
        .def("_put_device_attribute_property",
            &Tango::Database::put_device_attribute_property)
        .def("_put_device_pipe_property",
            &Tango::Database::put_device_pipe_property)
        .def("_delete_device_attribute_property",
            &Tango::Database::delete_device_attribute_property)
        .def("_delete_device_pipe_property",
            &Tango::Database::delete_device_pipe_property)
        .def("get_device_attribute_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &, const std::string &))
            &Tango::Database::get_device_attribute_property_history)
        .def("get_device_pipe_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &, const std::string &))
            &Tango::Database::get_device_pipe_property_history)
        .def("get_device_attribute_list",
            (void (Tango::Database::*) (const std::string &, StdStringVector &))
            &Tango::Database::get_device_attribute_list)
        .def("get_device_pipe_list",
            (void (Tango::Database::*) (const std::string &, StdStringVector &))
            &Tango::Database::get_device_pipe_list)
        .def("_get_class_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_class_property)
        .def("_put_class_property", &Tango::Database::put_class_property)
        .def("_delete_class_property", &Tango::Database::delete_class_property)
        .def("get_class_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_class_property_history)
        .def("get_class_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_class_list)
        .def("get_class_property_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_class_property_list)
        .def("_get_class_attribute_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_class_attribute_property)
        .def("_get_class_pipe_property",
            (void (Tango::Database::*) (std::string, Tango::DbData &))
            &Tango::Database::get_class_pipe_property)
        .def("_put_class_attribute_property",
            &Tango::Database::put_class_attribute_property)
        .def("_put_class_pipe_property",
            &Tango::Database::put_class_pipe_property)
        .def("_delete_class_attribute_property",
            &Tango::Database::delete_class_attribute_property)
        .def("_delete_class_pipe_property",
            &Tango::Database::delete_class_pipe_property)
        .def("get_class_attribute_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &, const std::string &))
            &Tango::Database::get_class_attribute_property_history)
        .def("get_class_pipe_property_history",
            (Tango::DbHistoryList (Tango::Database::*) (const std::string &, const std::string &, const std::string &))
            &Tango::Database::get_class_pipe_property_history)

        .def("get_class_attribute_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::get_class_attribute_list)
        .def("get_class_pipe_list", &Tango::Database::get_class_pipe_list)

        //
        // Attribute methods
        //

        .def("get_attribute_alias", &PyDatabase::get_attribute_alias)
        .def("get_attribute_alias_list",
            (Tango::DbDatum (Tango::Database::*) (const std::string &))
            &Tango::Database::get_attribute_alias_list)
        .def("put_attribute_alias",
            (void (Tango::Database::*) (const std::string &, const std::string &))
            &Tango::Database::put_attribute_alias)
        .def("delete_attribute_alias",
            (void (Tango::Database::*) (const std::string &))
            &Tango::Database::delete_attribute_alias)

        //
        // event methods
        //

        .def("export_event", &PyDatabase::export_event)
        .def("unexport_event",
            (void (Tango::Database::*) (const std::string &))
            &Tango::Database::unexport_event)

        //
        // alias methods
        //

        .def("get_device_from_alias", &PyDatabase::get_device_from_alias)
        .def("get_alias_from_device", &PyDatabase::get_alias_from_device)
        .def("get_attribute_from_alias", &PyDatabase::get_attribute_from_alias)
        .def("get_alias_from_attribute", &PyDatabase::get_alias_from_attribute)

        ;
}
