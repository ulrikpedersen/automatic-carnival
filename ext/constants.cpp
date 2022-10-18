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
#include "tango_numpy.h"
#include "tgutils.h"

// From https://gcc.gnu.org/onlinedocs/cpp/Stringizing.html
#define xstr(a) str(a)
#define str(a) #a

using namespace boost::python;

long TANGO_VERSION_HEX;

// Some internal constants were removed from cppTango in 9.4. To support both
// 9.4 and previous versions we must export constants conditionally, skipping
// the ones that are no longer available in cppTango. For each constant that 
// could missing we must define a dummy fallback value of the type specified
// below, in the global namespace. This type is later used to detect missing
// constants using a template specialization.
struct PyTangoFallbackConstant {};

static const PyTangoFallbackConstant MIN_POLL_PERIOD;
static const PyTangoFallbackConstant DELTA_T;
static const PyTangoFallbackConstant MIN_DELTA_WORK;
static const PyTangoFallbackConstant TIME_HEARTBEAT;
static const PyTangoFallbackConstant POLL_LOOP_NB;
static const PyTangoFallbackConstant ONE_SECOND;
static const PyTangoFallbackConstant DISCARD_THRESHOLD;

static const PyTangoFallbackConstant DELTA_PERIODIC;
static const PyTangoFallbackConstant DELTA_PERIODIC_LONG;

static const PyTangoFallbackConstant RECONNECTION_DELAY;

template <typename T>
static void export_conditionally(scope& consts_scope, const char* name, T value)
{
    consts_scope.attr(name) = value;
}

template <>
void export_conditionally(scope& /*consts_scope*/, const char* /*name*/, PyTangoFallbackConstant)
{
    // Do nothing for missing constants.
}

namespace Tango
{
static void export_optional_constants(scope& consts_scope)
{
    // This function must be defined in the Tango namespace and all constants
    // must be referenced using unqualified names. They are resolved either to
    // the proper constants provided by cppTango (if exist) or to the fallback
    // values defined in this file.

    //
    // Some general interest define
    //
    export_conditionally(consts_scope, "DELTA_T", DELTA_T);
    export_conditionally(consts_scope, "DELTA_T", DELTA_T);
    export_conditionally(consts_scope, "MIN_DELTA_WORK", MIN_DELTA_WORK);
    export_conditionally(consts_scope, "TIME_HEARTBEAT", TIME_HEARTBEAT);
    export_conditionally(consts_scope, "POLL_LOOP_NB", POLL_LOOP_NB);
    export_conditionally(consts_scope, "ONE_SECOND", ONE_SECOND);
    export_conditionally(consts_scope, "DISCARD_THRESHOLD", DISCARD_THRESHOLD);

    //
    // Event related define
    //
    export_conditionally(consts_scope, "DELTA_PERIODIC", DELTA_PERIODIC);
    export_conditionally(consts_scope, "DELTA_PERIODIC_LONG", DELTA_PERIODIC_LONG);

    //
    // Time to wait before trying to reconnect after
    // a connevtion failure
    //
    export_conditionally(consts_scope, "RECONNECTION_DELAY", RECONNECTION_DELAY);
}
}

void export_constants()
{
    object consts_module(handle<>(borrowed(PyImport_AddModule("tango.constants"))));
    scope().attr("constants") = consts_module;
    scope consts_scope = consts_module;

    consts_scope.attr("__doc__") = "module containing several Tango constants.\n"
        "\nNew in PyTango 7.0.0";

    consts_scope.attr("NUMPY_SUPPORT") = true;
    consts_scope.attr("NUMPY_VERSION") = xstr(PYTANGO_NUMPY_VERSION);

    consts_scope.attr("PY_MAJOR_VERSION") = PY_MAJOR_VERSION;
    consts_scope.attr("PY_MINOR_VERSION") = PY_MINOR_VERSION;
    consts_scope.attr("PY_MICRO_VERSION") = PY_MICRO_VERSION;
    consts_scope.attr("PY_VERSION") = PY_VERSION;
    consts_scope.attr("PY_VERSION_HEX") = PY_VERSION_HEX;

    consts_scope.attr("BOOST_MAJOR_VERSION") = BOOST_VERSION / 100000;
    consts_scope.attr("BOOST_MINOR_VERSION") = BOOST_VERSION / 100 % 1000;
    consts_scope.attr("BOOST_PATCH_VERSION") = BOOST_VERSION % 100;
    // missing BOOST_VERSION => do it in python


    //
    // From tango_const.h
    //

    Tango::export_optional_constants(consts_scope);

    //
    // Some general interest define
    //
    consts_scope.attr("TANGO_VERSION_MAJOR") = TANGO_VERSION_MAJOR;
    consts_scope.attr("TANGO_VERSION_MINOR") = TANGO_VERSION_MINOR;
    consts_scope.attr("TANGO_VERSION_PATCH") = TANGO_VERSION_PATCH;
    consts_scope.attr("TANGO_VERSION_NB") = TANGO_VERSION_NB;
    consts_scope.attr("TANGO_VERSION") = Tango::TgLibVers;

    consts_scope.attr("TgLibVers") = Tango::TgLibVers;
    consts_scope.attr("TgLibMajorVers") = Tango::TgLibMajorVers;
    consts_scope.attr("TgLibVersNb") = Tango::TgLibVersNb;
    consts_scope.attr("DevVersion") = Tango::DevVersion;
    consts_scope.attr("DefaultMaxSeq") = Tango::DefaultMaxSeq;
    consts_scope.attr("DefaultBlackBoxDepth") = Tango::DefaultBlackBoxDepth;
    consts_scope.attr("DefaultPollRingDepth") = Tango::DefaultPollRingDepth;

    consts_scope.attr("InitialOutput") =Tango:: InitialOutput;
    consts_scope.attr("DSDeviceDomain") = Tango::DSDeviceDomain;
    consts_scope.attr("DefaultDocUrl") = Tango::DefaultDocUrl;
    consts_scope.attr("EnvVariable") = Tango::EnvVariable;
    consts_scope.attr("WindowsEnvVariable") = Tango::WindowsEnvVariable;
    consts_scope.attr("DbObjName") = Tango::DbObjName;

    // Changed in tango 8 from DescNotSet to NotSet. We keep the old constant
    // to try to maintain backward compatibility
    consts_scope.attr("DescNotSet") = Tango::NotSet;
    consts_scope.attr("NotSet") = Tango::NotSet;

    consts_scope.attr("ResNotDefined") = Tango::ResNotDefined;
    consts_scope.attr("MessBoxTitle") = Tango::MessBoxTitle;
    consts_scope.attr("StatusNotSet") = Tango::StatusNotSet;
    consts_scope.attr("TangoHostNotSet") = Tango::TangoHostNotSet;
    consts_scope.attr("RootAttNotDef") = Tango::RootAttNotDef;

    consts_scope.attr("DefaultWritAttrProp") = Tango::DefaultWritAttrProp;
    consts_scope.attr("AllAttr") = Tango::AllAttr;
    consts_scope.attr("AllAttr_3") = Tango::AllAttr_3;
    consts_scope.attr("AllPipe") = Tango::AllPipe;
    consts_scope.attr("AllCmd") = Tango::AllCmd;

    consts_scope.attr("PollCommand") = Tango::PollCommand;
    consts_scope.attr("PollAttribute") = Tango::PollAttribute;

    consts_scope.attr("LOCAL_POLL_REQUEST") = Tango::LOCAL_POLL_REQUEST;
    consts_scope.attr("LOCAL_REQUEST_STR_SIZE") = Tango::LOCAL_REQUEST_STR_SIZE;

    consts_scope.attr("MIN_POLL_PERIOD") = Tango::MIN_POLL_PERIOD;

    consts_scope.attr("DEFAULT_TIMEOUT") = Tango::DEFAULT_TIMEOUT;
    consts_scope.attr("DEFAULT_POLL_OLD_FACTOR") = Tango::DEFAULT_POLL_OLD_FACTOR;

    consts_scope.attr("TG_IMP_MINOR_TO") = Tango::TG_IMP_MINOR_TO;
    consts_scope.attr("TG_IMP_MINOR_DEVFAILED") = Tango::TG_IMP_MINOR_DEVFAILED;
    consts_scope.attr("TG_IMP_MINOR_NON_DEVFAILED") = Tango::TG_IMP_MINOR_NON_DEVFAILED;

    consts_scope.attr("TANGO_PY_MOD_NAME") = Tango::TANGO_PY_MOD_NAME;
    consts_scope.attr("DATABASE_CLASS") = Tango::DATABASE_CLASS;

    consts_scope.attr("TANGO_FLOAT_PRECISION") = Tango::TANGO_FLOAT_PRECISION;
    consts_scope.attr("NoClass") = Tango::NoClass;

    //
    // Event related define
    //

    consts_scope.attr("EVENT_HEARTBEAT_PERIOD") = Tango::EVENT_HEARTBEAT_PERIOD;
    consts_scope.attr("EVENT_RESUBSCRIBE_PERIOD") = Tango::EVENT_RESUBSCRIBE_PERIOD;
    consts_scope.attr("DEFAULT_EVENT_PERIOD") = Tango::DEFAULT_EVENT_PERIOD;
    consts_scope.attr("HEARTBEAT") = Tango::HEARTBEAT;

    //
    // ZMQ event system related define
    //
    consts_scope.attr("ZMQ_EVENT_PROT_VERSION") = Tango::ZMQ_EVENT_PROT_VERSION;
    consts_scope.attr("HEARTBEAT_METHOD_NAME") = Tango::HEARTBEAT_METHOD_NAME;
    consts_scope.attr("EVENT_METHOD_NAME") = Tango::EVENT_METHOD_NAME;
    consts_scope.attr("HEARTBEAT_EVENT_NAME") = Tango::HEARTBEAT_EVENT_NAME;
    consts_scope.attr("CTRL_SOCK_ENDPOINT") = Tango::CTRL_SOCK_ENDPOINT;
    consts_scope.attr("MCAST_PROT") = Tango::MCAST_PROT;
    consts_scope.attr("MCAST_HOPS") = Tango::MCAST_HOPS;
    consts_scope.attr("PGM_RATE") = Tango::PGM_RATE;
    consts_scope.attr("PGM_IVL") = Tango::PGM_IVL;
    consts_scope.attr("MAX_SOCKET_SUB") = Tango::MAX_SOCKET_SUB;
    consts_scope.attr("PUB_HWM") = Tango::PUB_HWM;
    consts_scope.attr("SUB_HWM") = Tango::SUB_HWM;
    consts_scope.attr("SUB_SEND_HWM") = Tango::SUB_SEND_HWM;

    consts_scope.attr("NOTIFD_CHANNEL") = Tango::NOTIFD_CHANNEL;

    //
    // Locking feature related defines
    //

    consts_scope.attr("DEFAULT_LOCK_VALIDITY") = Tango::DEFAULT_LOCK_VALIDITY;
    consts_scope.attr("DEVICE_UNLOCKED_REASON") = Tango::DEVICE_UNLOCKED_REASON;
    consts_scope.attr("MIN_LOCK_VALIDITY") = Tango::MIN_LOCK_VALIDITY;
    consts_scope.attr("TG_LOCAL_HOST") = Tango::TG_LOCAL_HOST;

    //
    // Client timeout as defined by omniORB4.0.0
    //

    consts_scope.attr("CLNT_TIMEOUT_STR") = Tango::CLNT_TIMEOUT_STR;
    consts_scope.attr("CLNT_TIMEOUT") = Tango::CLNT_TIMEOUT;
    consts_scope.attr("NARROW_CLNT_TIMEOUT") = Tango::NARROW_CLNT_TIMEOUT;

    //
    // Connection and call timeout for database device
    //

    consts_scope.attr("DB_CONNECT_TIMEOUT") = Tango::DB_CONNECT_TIMEOUT;
    consts_scope.attr("DB_RECONNECT_TIMEOUT") = Tango::DB_RECONNECT_TIMEOUT;
    consts_scope.attr("DB_TIMEOUT") = Tango::DB_TIMEOUT;
    consts_scope.attr("DB_START_PHASE_RETRIES") = Tango::DB_START_PHASE_RETRIES;

    //
    // Access Control related defines
    // WARNING: these string are also used within the Db stored procedure
    // introduced in Tango V6.1. If you chang eit here, don't forget to
    // also update the stored procedure
    //

    consts_scope.attr("CONTROL_SYSTEM") = Tango::CONTROL_SYSTEM;
    consts_scope.attr("SERVICE_PROP_NAME") = Tango::SERVICE_PROP_NAME;
    consts_scope.attr("ACCESS_SERVICE") = Tango::ACCESS_SERVICE;

    //
    // Polling threads pool related defines
    //

    consts_scope.attr("DEFAULT_POLLING_THREADS_POOL_SIZE") = Tango::DEFAULT_POLLING_THREADS_POOL_SIZE;

    //
    // Max transfer size 256 MBytes (in byte). Needed by omniORB
    //

    consts_scope.attr("MAX_TRANSFER_SIZE") = Tango::MAX_TRANSFER_SIZE;

    //
    // Max GIOP connection per server . Needed by omniORB
    //

    consts_scope.attr("MAX_GIOP_PER_SERVER") = Tango::MAX_GIOP_PER_SERVER;

    //
    // Tango name length
    //

    consts_scope.attr("MaxServerNameLength") = Tango::MaxServerNameLength;
    consts_scope.attr("MaxDevPropLength") = Tango::MaxDevPropLength;

    //
    // For forwarded attribute implementation
    //
    consts_scope.attr("MIN_IDL_CONF5") = Tango::MIN_IDL_CONF5;
    consts_scope.attr("MIN_IDL_DEV_INTR") = Tango::MIN_IDL_DEV_INTR;
    consts_scope.attr("ALL_EVENTS") = Tango::ALL_EVENTS;

    // --------------------------------------------------------

    //
    // Files used to retrieve env. variables
    //

    consts_scope.attr("USER_ENV_VAR_FILE") = Tango::USER_ENV_VAR_FILE;

    consts_scope.attr("kLogTargetConsole") = Tango::kLogTargetConsole;
    consts_scope.attr("kLogTargetFile") = Tango::kLogTargetFile;
    consts_scope.attr("kLogTargetDevice") = Tango::kLogTargetDevice;
    consts_scope.attr("kLogTargetSep") = Tango::kLogTargetSep;

    consts_scope.attr("AlrmValueNotSpec") = Tango::AlrmValueNotSpec;
    consts_scope.attr("AssocWritNotSpec") = Tango::AssocWritNotSpec;
    consts_scope.attr("LabelNotSpec") = Tango::LabelNotSpec;
    consts_scope.attr("DescNotSpec") = Tango::DescNotSpec;
    consts_scope.attr("UnitNotSpec") = Tango::UnitNotSpec;
    consts_scope.attr("StdUnitNotSpec") = Tango::StdUnitNotSpec;
    consts_scope.attr("DispUnitNotSpec") = Tango::DispUnitNotSpec;
#ifdef FormatNotSpec
    consts_scope.attr("FormatNotSpec") = Tango::FormatNotSpec;
#else
    consts_scope.attr("FormatNotSpec") = Tango::FormatNotSpec_FL;
#endif
    consts_scope.attr("FormatNotSpec_FL") = Tango::FormatNotSpec_FL;
    consts_scope.attr("FormatNotSpec_INT") = Tango::FormatNotSpec_INT;
    consts_scope.attr("FormatNotSpec_STR") = Tango::FormatNotSpec_STR;

    consts_scope.attr("NotANumber") = Tango::NotANumber;
    consts_scope.attr("MemNotUsed") = Tango::MemNotUsed;
    consts_scope.attr("MemAttrPropName") = Tango::MemAttrPropName;

    consts_scope.attr("API_AttrConfig") = Tango::API_AttrConfig;
    consts_scope.attr("API_AttrEventProp") = Tango::API_AttrEventProp;
    consts_scope.attr("API_AttrIncorrectDataNumber") = Tango::API_AttrIncorrectDataNumber;
    consts_scope.attr("API_AttrNoAlarm") = Tango::API_AttrNoAlarm;
    consts_scope.attr("API_AttrNotAllowed") = Tango::API_AttrNotAllowed;
    consts_scope.attr("API_AttrNotFound") = Tango::API_AttrNotFound;
    consts_scope.attr("API_AttrNotWritable") = Tango::API_AttrNotWritable;
    consts_scope.attr("API_AttrOptProp") = Tango::API_AttrOptProp;
    consts_scope.attr("API_AttrPropValueNotSet") = Tango::API_AttrPropValueNotSet;
    consts_scope.attr("API_AttrValueNotSet") = Tango::API_AttrValueNotSet;
    consts_scope.attr("API_AttrWrongDefined") = Tango::API_AttrWrongDefined;
    consts_scope.attr("API_AttrWrongMemValue") = Tango::API_AttrWrongMemValue;
    consts_scope.attr("API_BadConfigurationProperty") = Tango::API_BadConfigurationProperty;
    consts_scope.attr("API_BlackBoxArgument") = Tango::API_BlackBoxArgument;
    consts_scope.attr("API_BlackBoxEmpty") = Tango::API_BlackBoxEmpty;
    consts_scope.attr("API_CannotCheckAccessControl") = Tango::API_CannotCheckAccessControl;
    consts_scope.attr("API_CannotOpenFile") = Tango::API_CannotOpenFile;
    consts_scope.attr("API_CantActivatePOAManager") = Tango::API_CantActivatePOAManager;
    consts_scope.attr("API_CantCreateClassPoa") = Tango::API_CantCreateClassPoa;
    consts_scope.attr("API_CantCreateLockingThread") = Tango::API_CantCreateLockingThread;
    consts_scope.attr("API_CantFindLockingThread") = Tango::API_CantFindLockingThread;
    consts_scope.attr("API_CantGetClientIdent") = Tango::API_CantGetClientIdent;
    consts_scope.attr("API_CantGetDevObjectId") = Tango::API_CantGetDevObjectId;
    consts_scope.attr("API_CantInstallSignal") = Tango::API_CantInstallSignal;
    consts_scope.attr("API_CantRetrieveClass") = Tango::API_CantRetrieveClass;
    consts_scope.attr("API_CantRetrieveClassList") = Tango::API_CantRetrieveClassList;
    consts_scope.attr("API_CantStoreDeviceClass") = Tango::API_CantStoreDeviceClass;
    consts_scope.attr("API_ClassNotFound") = Tango::API_ClassNotFound;
    consts_scope.attr("API_CmdArgumentTypeNotSupported") = Tango::API_CmdArgumentTypeNotSupported;
    consts_scope.attr("API_CommandNotAllowed") = Tango::API_CommandNotAllowed;
    consts_scope.attr("API_CommandNotFound") = Tango::API_CommandNotFound;
    consts_scope.attr("API_CorbaSysException") = Tango::API_CorbaSysException;
    consts_scope.attr("API_CorruptedDatabase") = Tango::API_CorruptedDatabase;
    consts_scope.attr("API_DatabaseAccess") = Tango::API_DatabaseAccess;
    consts_scope.attr("API_DeviceLocked") = Tango::API_DeviceLocked;
    consts_scope.attr("API_DeviceNotFound") = Tango::API_DeviceNotFound;
    consts_scope.attr("API_DeviceNotLocked") = Tango::API_DeviceNotLocked;
    consts_scope.attr("API_DeviceUnlockable") = Tango::API_DeviceUnlockable;
    consts_scope.attr("API_DeviceUnlocked") = Tango::API_DeviceUnlocked;
    consts_scope.attr("API_EventSupplierNotConstructed") = Tango::API_EventSupplierNotConstructed;
    consts_scope.attr("API_IncoherentDbData") = Tango::API_IncoherentDbData;
    consts_scope.attr("API_IncoherentDevData") = Tango::API_IncoherentDevData;
    consts_scope.attr("API_IncoherentValues") = Tango::API_IncoherentValues;
    consts_scope.attr("API_IncompatibleAttrDataType") = Tango::API_IncompatibleAttrDataType;
    consts_scope.attr("API_IncompatibleCmdArgumentType") = Tango::API_IncompatibleCmdArgumentType;
    consts_scope.attr("API_InitMethodNotFound") = Tango::API_InitMethodNotFound;
    consts_scope.attr("API_InitNotPublic") = Tango::API_InitNotPublic;
    consts_scope.attr("API_InitThrowsException") = Tango::API_InitThrowsException;
    consts_scope.attr("API_JavaRuntimeSecurityException") = Tango::API_JavaRuntimeSecurityException;
    consts_scope.attr("API_MemoryAllocation") = Tango::API_MemoryAllocation;
    consts_scope.attr("API_MethodArgument") = Tango::API_MethodArgument;
    consts_scope.attr("API_MethodNotFound") = Tango::API_MethodNotFound;
    consts_scope.attr("API_MissedEvents") = Tango::API_MissedEvents;
    consts_scope.attr("API_NotSupportedFeature") = Tango::API_NotSupportedFeature;
    consts_scope.attr("API_NtDebugWindowError") = Tango::API_NtDebugWindowError;
    consts_scope.attr("API_OverloadingNotSupported") = Tango::API_OverloadingNotSupported;
    consts_scope.attr("API_PolledDeviceNotInPoolConf") = Tango::API_PolledDeviceNotInPoolConf;
    consts_scope.attr("API_PolledDeviceNotInPoolMap") = Tango::API_PolledDeviceNotInPoolMap;
    consts_scope.attr("API_PollingThreadNotFound") = Tango::API_PollingThreadNotFound;
    consts_scope.attr("API_ReadOnlyMode") = Tango::API_ReadOnlyMode;
    consts_scope.attr("API_SignalOutOfRange") = Tango::API_SignalOutOfRange;
    consts_scope.attr("API_SystemCallFailed") = Tango::API_SystemCallFailed;
    consts_scope.attr("API_WAttrOutsideLimit") = Tango::API_WAttrOutsideLimit;
    consts_scope.attr("API_WizardConfError") = Tango::API_WizardConfError;
    consts_scope.attr("API_WrongEventData") = Tango::API_WrongEventData;
    consts_scope.attr("API_WrongHistoryDataBuffer") = Tango::API_WrongHistoryDataBuffer;
    consts_scope.attr("API_WrongLockingStatus") = Tango::API_WrongLockingStatus;
    consts_scope.attr("API_ZmqInitFailed") = Tango::API_ZmqInitFailed;

}
