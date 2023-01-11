#include <string>

#include "pytango/pytango.hpp"

#include <tango/tango.h>
exported_class::exported_class()
    : m_name {"pytango"}
{
}

auto exported_class::name() const -> const char*
{
  return m_name.c_str();
}

auto exported_class::addnumbers(int one, int two) const -> int
{
  const int result = one + two;
  Tango::DeviceProxy *device = new Tango::DeviceProxy("sys/database/2"); // just enough to link against libtango

  return result;
}