#include <string>

#include "pytango/pytango.hpp"

auto main() -> int
{
  auto const exported = exported_class {};

  return std::string("pytango") == exported.name() ? 0 : 1;
}
