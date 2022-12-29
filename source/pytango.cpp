#include <string>

#include "pytango/pytango.hpp"

exported_class::exported_class()
    : m_name {"pytango"}
{
}

auto exported_class::name() const -> const char*
{
  return m_name.c_str();
}

auto exported_class::addnumbers(int one, int two) -> int
{
  const int result = one + two;
  return result;
}