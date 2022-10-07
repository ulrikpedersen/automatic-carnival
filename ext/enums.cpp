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

#include <boost/utility/enable_if.hpp>

using namespace boost::python;

// This file exposes cppTango enumeration types which are usually defined in
// tango_const.h.in. A special handling is needed for LogLevel and LogTarget
// as these two enums may not be defined in cppTango 9.3 if it was compiled
// without TANGO_HAS_LOG4TANGO set.

// A fallback type if it is not defined by cppTango in the Tango namespace.
// For the SFINAE below to work as intended, the size of cppTango's LogLevel
// must be different from 1 (right now it is sizeof(int) = 4).
typedef char LogLevel;
typedef char LogTarget;

// Fallback enum values. These are not really needed but compiler needs to be
// able to resolve names when it parses the template specialization (even if
// it is later rejected by enable_if).
static const int LOG_OFF = 0;
static const int LOG_FATAL = 0;
static const int LOG_ERROR = 0;
static const int LOG_WARN = 0;
static const int LOG_INFO = 0;
static const int LOG_DEBUG = 0;

static const int LOG_CONSOLE = 0;
static const int LOG_FILE = 0;
static const int LOG_DEVICE = 0;

namespace Tango
{
    struct PyTangoLogEnums
    {
        typedef LogLevel LogLevelT;
        typedef LogTarget LogTargetT;
    };

    // Accessors for enum values. If Tango does not provide those,
    // fallback values from the global namespace will be used.
    static LogLevel pytango_enum_log_off() { return LOG_OFF; }
    static LogLevel pytango_enum_log_fatal() { return LOG_FATAL; }
    static LogLevel pytango_enum_log_error() { return LOG_ERROR; }
    static LogLevel pytango_enum_log_warn() { return LOG_WARN; }
    static LogLevel pytango_enum_log_info() { return LOG_INFO; }
    static LogLevel pytango_enum_log_debug() { return LOG_DEBUG; }
    static LogTarget pytango_enum_log_console() { return LOG_CONSOLE; }
    static LogTarget pytango_enum_log_file() { return LOG_FILE; }
    static LogTarget pytango_enum_log_device() { return LOG_DEVICE; }
}

template <typename T, typename = void>
struct Log4TangoEnums
{
    static void export_enums()
    {
        // By default do nothing.
    }
};

template <typename T>
struct Log4TangoEnums<T,
    typename boost::enable_if_c<(sizeof(typename T::LogLevelT) != 1)>::type>
{
    static void export_enums()
    {
        enum_<typename T::LogLevelT>("LogLevel")
            .value("LOG_OFF", Tango::pytango_enum_log_off())
            .value("LOG_FATAL", Tango::pytango_enum_log_fatal())
            .value("LOG_ERROR", Tango::pytango_enum_log_error())
            .value("LOG_WARN", Tango::pytango_enum_log_warn())
            .value("LOG_INFO", Tango::pytango_enum_log_info())
            .value("LOG_DEBUG", Tango::pytango_enum_log_debug())
        ;

        // We assume that LogTarget is also available if LogLevel is available.
        enum_<typename T::LogTargetT>("LogTarget")
            .value("LOG_CONSOLE", Tango::pytango_enum_log_console())
            .value("LOG_FILE", Tango::pytango_enum_log_file())
            .value("LOG_DEVICE", Tango::pytango_enum_log_device())
        ;
    }
};

void export_enums()
{
    enum_<Tango::LockerLanguage>("LockerLanguage")
        .value("CPP", Tango::CPP)
        .value("JAVA", Tango::JAVA)
    ;

    enum_<Tango::CmdArgType>("CmdArgType")
        .value(Tango::CmdArgTypeName[Tango::DEV_VOID], Tango::DEV_VOID)
        .value(Tango::CmdArgTypeName[Tango::DEV_BOOLEAN], Tango::DEV_BOOLEAN)
        .value(Tango::CmdArgTypeName[Tango::DEV_SHORT], Tango::DEV_SHORT)
        .value(Tango::CmdArgTypeName[Tango::DEV_LONG], Tango::DEV_LONG)
        .value(Tango::CmdArgTypeName[Tango::DEV_FLOAT], Tango::DEV_FLOAT)
        .value(Tango::CmdArgTypeName[Tango::DEV_DOUBLE], Tango::DEV_DOUBLE)
        .value(Tango::CmdArgTypeName[Tango::DEV_USHORT], Tango::DEV_USHORT)
        .value(Tango::CmdArgTypeName[Tango::DEV_ULONG], Tango::DEV_ULONG)
        .value(Tango::CmdArgTypeName[Tango::DEV_STRING], Tango::DEV_STRING)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_CHARARRAY], Tango::DEVVAR_CHARARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_SHORTARRAY], Tango::DEVVAR_SHORTARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_LONGARRAY], Tango::DEVVAR_LONGARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_FLOATARRAY], Tango::DEVVAR_FLOATARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_DOUBLEARRAY], Tango::DEVVAR_DOUBLEARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_USHORTARRAY], Tango::DEVVAR_USHORTARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_ULONGARRAY], Tango::DEVVAR_ULONGARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_STRINGARRAY], Tango::DEVVAR_STRINGARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_LONGSTRINGARRAY], Tango::DEVVAR_LONGSTRINGARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_DOUBLESTRINGARRAY], Tango::DEVVAR_DOUBLESTRINGARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEV_STATE], Tango::DEV_STATE)
        .value(Tango::CmdArgTypeName[Tango::CONST_DEV_STRING], Tango::CONST_DEV_STRING)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_BOOLEANARRAY], Tango::DEVVAR_BOOLEANARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEV_UCHAR], Tango::DEV_UCHAR)
        .value(Tango::CmdArgTypeName[Tango::DEV_LONG64], Tango::DEV_LONG64)
        .value(Tango::CmdArgTypeName[Tango::DEV_ULONG64], Tango::DEV_ULONG64)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_LONG64ARRAY], Tango::DEVVAR_LONG64ARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_ULONG64ARRAY], Tango::DEVVAR_ULONG64ARRAY)
        .value(Tango::CmdArgTypeName[Tango::DEV_INT], Tango::DEV_INT)
        .value(Tango::CmdArgTypeName[Tango::DEV_ENCODED], Tango::DEV_ENCODED)
        .value(Tango::CmdArgTypeName[Tango::DEV_ENUM], Tango::DEV_ENUM)
        .value(Tango::CmdArgTypeName[Tango::DEV_PIPE_BLOB], Tango::DEV_PIPE_BLOB)
        .value(Tango::CmdArgTypeName[Tango::DEVVAR_STATEARRAY], Tango::DEVVAR_STATEARRAY)
        .export_values()
    ;

    enum_<Tango::MessBoxType>("MessBoxType")
        .value("STOP", Tango::STOP)
        .value("INFO", Tango::INFO)
    ;

    enum_<Tango::PollObjType>("PollObjType")
        .value("POLL_CMD", Tango::POLL_CMD)
        .value("POLL_ATTR", Tango::POLL_ATTR)
        .value("EVENT_HEARTBEAT", Tango::EVENT_HEARTBEAT)
        .value("STORE_SUBDEV", Tango::STORE_SUBDEV)
    ;

    enum_<Tango::PollCmdCode>("PollCmdCode")
        .value("POLL_ADD_OBJ", Tango::POLL_ADD_OBJ)
        .value("POLL_REM_OBJ", Tango::POLL_REM_OBJ)
        .value("POLL_START", Tango::POLL_START)
        .value("POLL_STOP", Tango::POLL_STOP)
        .value("POLL_UPD_PERIOD", Tango::POLL_UPD_PERIOD)
        .value("POLL_REM_DEV", Tango::POLL_REM_DEV)
        .value("POLL_EXIT", Tango::POLL_EXIT)
        .value("POLL_REM_EXT_TRIG_OBJ", Tango::POLL_REM_EXT_TRIG_OBJ)
        .value("POLL_ADD_HEARTBEAT", Tango::POLL_ADD_HEARTBEAT)
        .value("POLL_REM_HEARTBEAT", Tango::POLL_REM_HEARTBEAT)
    ;

    enum_<Tango::SerialModel>("SerialModel")
        .value("BY_DEVICE",Tango::BY_DEVICE)
        .value("BY_CLASS",Tango::BY_CLASS)
        .value("BY_PROCESS",Tango::BY_PROCESS)
        .value("NO_SYNC",Tango::NO_SYNC)
    ;

    enum_<Tango::AttReqType>("AttReqType")
        .value("READ_REQ",Tango::READ_REQ)
        .value("WRITE_REQ",Tango::WRITE_REQ)
    ;

    enum_<Tango::LockCmdCode>("LockCmdCode")
        .value("LOCK_ADD_DEV", Tango::LOCK_ADD_DEV)
        .value("LOCK_REM_DEV", Tango::LOCK_REM_DEV)
        .value("LOCK_UNLOCK_ALL_EXIT", Tango::LOCK_UNLOCK_ALL_EXIT)
        .value("LOCK_EXIT", Tango::LOCK_EXIT)
    ;

    Log4TangoEnums<Tango::PyTangoLogEnums>::export_enums();

    enum_<Tango::EventType>("EventType")
        .value("CHANGE_EVENT", Tango::CHANGE_EVENT)
        .value("QUALITY_EVENT", Tango::QUALITY_EVENT)
        .value("PERIODIC_EVENT", Tango::PERIODIC_EVENT)
        .value("ARCHIVE_EVENT", Tango::ARCHIVE_EVENT)
        .value("USER_EVENT", Tango::USER_EVENT)
        .value("ATTR_CONF_EVENT", Tango::ATTR_CONF_EVENT)
        .value("DATA_READY_EVENT", Tango::DATA_READY_EVENT)
        .value("INTERFACE_CHANGE_EVENT", Tango::INTERFACE_CHANGE_EVENT)
        .value("PIPE_EVENT", Tango::PIPE_EVENT)
    ;

    enum_<Tango::AttrSerialModel>("AttrSerialModel")
        .value("ATTR_NO_SYNC", Tango::ATTR_NO_SYNC)
        .value("ATTR_BY_KERNEL", Tango::ATTR_BY_KERNEL)
        .value("ATTR_BY_USER", Tango::ATTR_BY_USER)
    ;
    
    enum_<Tango::KeepAliveCmdCode>("KeepAliveCmdCode")
        .value("EXIT_TH", Tango::EXIT_TH)
    ;

    enum_<Tango::AccessControlType>("AccessControlType")
        .value("ACCESS_READ", Tango::ACCESS_READ)
        .value("ACCESS_WRITE", Tango::ACCESS_WRITE)
    ;

    enum_<Tango::asyn_req_type>("asyn_req_type")
        .value("POLLING", Tango::POLLING)
        .value("CALLBACK", Tango::CALL_BACK)
        .value("ALL_ASYNCH", Tango::ALL_ASYNCH)
    ;

    enum_<Tango::cb_sub_model>("cb_sub_model")
        .value("PUSH_CALLBACK", Tango::PUSH_CALLBACK)
        .value("PULL_CALLBACK", Tango::PULL_CALLBACK)
    ;

    //
    // Tango IDL
    //

    enum_<Tango::AttrQuality>("AttrQuality")
        .value("ATTR_VALID", Tango::ATTR_VALID)
        .value("ATTR_INVALID", Tango::ATTR_INVALID)
        .value("ATTR_ALARM", Tango::ATTR_ALARM)
        .value("ATTR_CHANGING", Tango::ATTR_CHANGING)
        .value("ATTR_WARNING", Tango::ATTR_WARNING)
    ;

    enum_<Tango::AttrWriteType>("AttrWriteType")
        .value("READ", Tango::READ)
        .value("READ_WITH_WRITE", Tango::READ_WITH_WRITE)
        .value("WRITE", Tango::WRITE)
        .value("READ_WRITE", Tango::READ_WRITE)
        .value("WT_UNKNOWN", Tango::WT_UNKNOWN)
        .export_values()
    ;

    enum_<Tango::AttrDataFormat>("AttrDataFormat")
        .value("SCALAR", Tango::SCALAR)
        .value("SPECTRUM", Tango::SPECTRUM)
        .value("IMAGE", Tango::IMAGE)
        .value("FMT_UNKNOWN", Tango::FMT_UNKNOWN)
        .export_values()
    ;

    enum_<Tango::DevSource>("DevSource")
        .value("DEV", Tango::DEV)
        .value("CACHE", Tango::CACHE)
        .value("CACHE_DEV", Tango::CACHE_DEV)
    ;

    enum_<Tango::ErrSeverity>("ErrSeverity")
        .value("WARN", Tango::WARN)
        .value("ERR", Tango::ERR)
        .value("PANIC", Tango::PANIC)
    ;

    enum_<Tango::DevState>("DevState")
        .value(Tango::DevStateName[Tango::ON], Tango::ON)
        .value(Tango::DevStateName[Tango::OFF], Tango::OFF)
        .value(Tango::DevStateName[Tango::CLOSE], Tango::CLOSE)
        .value(Tango::DevStateName[Tango::OPEN], Tango::OPEN)
        .value(Tango::DevStateName[Tango::INSERT], Tango::INSERT)
        .value(Tango::DevStateName[Tango::EXTRACT], Tango::EXTRACT)
        .value(Tango::DevStateName[Tango::MOVING], Tango::MOVING)
        .value(Tango::DevStateName[Tango::STANDBY], Tango::STANDBY)
        .value(Tango::DevStateName[Tango::FAULT], Tango::FAULT)
        .value(Tango::DevStateName[Tango::INIT], Tango::INIT)
        .value(Tango::DevStateName[Tango::RUNNING], Tango::RUNNING)
        .value(Tango::DevStateName[Tango::ALARM], Tango::ALARM)
        .value(Tango::DevStateName[Tango::DISABLE], Tango::DISABLE)
        .value(Tango::DevStateName[Tango::UNKNOWN], Tango::UNKNOWN)
    ;

    enum_<Tango::DispLevel>("DispLevel")
        .value("OPERATOR", Tango::OPERATOR)
        .value("EXPERT", Tango::EXPERT)
        .value("DL_UNKNOWN", Tango::DL_UNKNOWN)
    ;

    enum_<Tango::PipeWriteType>("PipeWriteType")
        .value("PIPE_READ", Tango::PIPE_READ)
        .value("PIPE_READ_WRITE", Tango::PIPE_READ_WRITE)
        .value("PIPE_WT_UNKNOWN", Tango::PIPE_WT_UNKNOWN)
    ;

    enum_<Tango::PipeSerialModel>("PipeSerialModel")
        .value("PIPE_NO_SYNC", Tango::PIPE_NO_SYNC)
        .value("PIPE_BY_KERNEL", Tango::PIPE_BY_KERNEL)
        .value("PIPE_BY_USER", Tango::PIPE_BY_USER)
    ;
  
    scope().attr("PipeReqType") = scope().attr("AttReqType");

    enum_<Tango::AttrMemorizedType>("AttrMemorizedType")
        .value("NOT_KNOWN", Tango::NOT_KNOWN)
        .value("NONE", Tango::NONE)
        .value("MEMORIZED", Tango::MEMORIZED)
        .value("MEMORIZED_WRITE_INIT", Tango::MEMORIZED_WRITE_INIT)
    ;
}
