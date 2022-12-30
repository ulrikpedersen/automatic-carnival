#include <string>

#include "pytango/pytango.hpp"

auto main() -> int
{
  auto const exported = exported_class {};
  if (exported.addnumbers(1, 2) != 3) {
    return 1;
  }
  return std::string("pytango") == exported.name() ? 0 : 1;
}
