/******************************************************************************
  This file is part of PyTango (http://pytango.rtfd.io)

  Copyright 2006-2012 CELLS / ALBA Synchrotron, Bellaterra, Spain
  Copyright 2013-2014 European Synchrotron Radiation Facility, Grenoble, France

  Distributed under the terms of the GNU Lesser General Public License,
  either version 3 of the License, or (at your option) any later version.
  See LICENSE.txt for more info.
******************************************************************************/

#pragma once

#include <boost/python.hpp>
#include <tango/tango.h>
#include <omnithread.h>

namespace bopy = boost::python;

#define arg_(a) boost::python::arg(a)


inline PyObject *PyObject_GetAttrString_(PyObject *o, const std::string &attr_name)
{
    const char *attr = attr_name.c_str();
    return PyObject_GetAttrString(o, attr);
}

inline PyObject *PyImport_ImportModule_(const std::string &name)
{
    const char *attr = name.c_str();
    return PyImport_ImportModule(attr);
}

// Bytes interface
#include <bytesobject.h>


PyObject* from_char_to_python_str(const char* in, Py_ssize_t size=-1,
                                  const char* encoding=NULL, /* defaults to latin-1 */
                                  const char* errors="strict");

PyObject* from_char_to_python_str(const std::string& in,
                                  const char* encoding=NULL, /* defaults to latin-1 */
                                  const char* errors="strict");

bopy::object from_char_to_boost_str(const char* in, Py_ssize_t size=-1,
                                    const char* encoding=NULL, /* defaults to latin-1 */
                                    const char* errors="strict");

bopy::object from_char_to_boost_str(const std::string& in,
                                    const char* encoding=NULL, /* defaults to latin-1 */
                                    const char* errors="strict");


void from_str_to_char(const bopy::object& in, std::string& out);
void from_str_to_char(PyObject* in, std::string& out);
char* from_str_to_char(PyObject* in);
char* from_str_to_char(const bopy::object& in);

inline void raise_(PyObject *type, const char *message)
{
    PyErr_SetString(type, message);
    boost::python::throw_error_already_set();
}

/// You should run any I/O intensive operations (like requesting data through
/// the network) in the context of an object like this.
class AutoPythonAllowThreads
{
    PyThreadState *m_save;

public:

    inline void giveup()
    {
        if (m_save)
        {
            PyEval_RestoreThread(m_save);
            m_save = 0;
        }
    }

    inline AutoPythonAllowThreads()
    {
        m_save = PyEval_SaveThread();
    }

    inline ~AutoPythonAllowThreads()
    {
        giveup();
    }
};

// Delete a pointer for a CppTango class with Python GIL released.
// Typically used by boost::shared_ptr constructors as the function
// to call when the object is deleted.
struct DeleterWithoutGIL {
    template <typename T>
    void operator()(T* ptr) {
        AutoPythonAllowThreads guard;
        delete ptr;
    }
};

/// The following class ensures usage in a non-omniORB thread will
/// still get a dummy omniORB thread ID - cppTango requires threads to
/// be identifiable in this way.  It should only be acquired once for the
/// lifetime of the thread, and must be released before the thread is
/// cleaned up.
/// See https://github.com/tango-controls/pytango/issues/307
class EnsureOmniThread
{
    omni_thread::ensure_self *ensure_self;

public:
    inline EnsureOmniThread()
    {
        ensure_self = NULL;
    }

    inline void acquire()
    {
        if (ensure_self == NULL)
        {
          ensure_self = new omni_thread::ensure_self;
        }
    }

    inline void release()
    {
        if (ensure_self != NULL)
        {
          delete ensure_self;
          ensure_self = NULL;
        }
    }

    inline ~EnsureOmniThread()
    {
      release();
    }

};

/**
 * Determines if the calling thread is (or looks like) an omniORB thread.
 *
 * @return returns true if the calling thread has an omniORB thread ID or false otherwise
 */
inline bool is_omni_thread()
{
    omni_thread *thread_id = omni_thread::self();
    return (thread_id != NULL);
};

/**
 * Determines if the given method name exists and is callable
 * within the python class
 *
 * @param[in] obj object to search for the method
 * @param[in] method_name the name of the method
 *
 * @return returns true is the method exists or false otherwise
 */
bool is_method_defined(boost::python::object &obj, const std::string &method_name);

/**
 * Determines if the given method name exists and is callable
 * within the python class
 *
 * @param[in] obj object to search for the method
 * @param[in] method_name the name of the method
 *
 * @return returns true is the method exists or false otherwise
 */
bool is_method_defined(PyObject *obj, const std::string &method_name);

/**
 * Determines if the given method name exists and is callable
 * within the python class
 *
 * @param[in] obj object to search for the method
 * @param[in] method_name the name of the method
 * @param[out] exists set to true if the symbol exists or false otherwise
 * @param[out] is_method set to true if the symbol exists and is a method
 *             or false otherwise
 */
void is_method_defined(PyObject *obj, const std::string &method_name,
                       bool &exists, bool &is_method);

/**
 * Determines if the given method name exists and is callable
 * within the python class
 *
 * @param[in] obj object to search for the method
 * @param[in] method_name the name of the method
 * @param[out] exists set to true if the symbol exists or false otherwise
 * @param[out] is_method set to true if the symbol exists and is a method
 *             or false otherwise
 */
void is_method_defined(boost::python::object &obj, const std::string &method_name,
                       bool &exists, bool &is_method);

#define PYTANGO_MOD \
    boost::python::object pytango((boost::python::handle<>(boost::python::borrowed(PyImport_AddModule("tango")))));

#define CALL_METHOD(retType, self, name, ...) \
    boost::python::call_method<retType>(self, name , __VA_ARGS__);


bool hasattr(boost::python::object &, const std::string &);
