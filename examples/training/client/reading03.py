#!/usr/bin/env python3
#
# client example: reading an attribute, example with spectrum

import sys
from tango import DeviceProxy, DevFailed, Except

dev_name = "sys/tg_test/1"
attr_name = "float_spectrum_ro"

# step 1 create the device proxy
try:
    dev = DeviceProxy(dev_name)
    print(f"proxy for {dev_name} created")
except DevFailed as ex:
    Except.print_exception(ex)
    sys.exit(1)  # simplistic error handling

# step 2 read the attribute
try:
    da = dev.read_attribute(attr_name)
    values = da.value
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to read attribute")
    sys.exit(1)  # simplistic error handling

print(f"{dev_name}/{attr_name} values:")
# very simple handling of Spectrum (or vector...)
for index, value in enumerate(values):
    print(f"values[{index}]: {value}")

"""
Typical output:

➜  training git:(develop) ✗ docker-compose exec cli /training/client/reading03.py
proxy for sys/tg_test/1 created
sys/tg_test/1/float_spectrum_ro values:
values[0]: 70.0
values[1]: 130.0
values[2]: 221.0
values[3]: 27.0
values[4]: 226.0
values[5]: 12.0
values[6]: 101.0
values[7]: 78.0
values[8]: 72.0
values[9]: 123.0
values[10]: 162.0
values[11]: 178.0
values[12]: 6.0
values[13]: 22.0
values[14]: 65.0
values[15]: 153.0
values[16]: 20.0
values[17]: 34.0
values[18]: 121.0
values[19]: 48.0
values[20]: 58.0
values[21]: 115.0
values[22]: 125.0
values[23]: 16.0
values[24]: 246.0
values[25]: 78.0
values[26]: 91.0
values[27]: 54.0
values[28]: 63.0
values[29]: 69.0
values[30]: 17.0
values[31]: 134.0
values[32]: 199.0
values[33]: 239.0
values[34]: 161.0
values[35]: 169.0
values[36]: 251.0
values[37]: 6.0
values[38]: 247.0
values[39]: 68.0
values[40]: 129.0
values[41]: 154.0
values[42]: 246.0
values[43]: 136.0
values[44]: 176.0
values[45]: 55.0
values[46]: 33.0
values[47]: 196.0
values[48]: 89.0
values[49]: 154.0
values[50]: 245.0
values[51]: 147.0
values[52]: 13.0
values[53]: 114.0
values[54]: 163.0
values[55]: 4.0
values[56]: 192.0
values[57]: 255.0
values[58]: 58.0
values[59]: 0.0
values[60]: 68.0
values[61]: 75.0
values[62]: 134.0
values[63]: 11.0
values[64]: 58.0
values[65]: 39.0
values[66]: 181.0
values[67]: 54.0
values[68]: 46.0
values[69]: 172.0
values[70]: 122.0
values[71]: 175.0
values[72]: 70.0
values[73]: 112.0
values[74]: 55.0
values[75]: 246.0
values[76]: 168.0
values[77]: 88.0
values[78]: 187.0
values[79]: 1.0
values[80]: 243.0
values[81]: 176.0
values[82]: 149.0
values[83]: 0.0
values[84]: 34.0
values[85]: 56.0
values[86]: 4.0
values[87]: 226.0
values[88]: 55.0
values[89]: 62.0
values[90]: 226.0
values[91]: 123.0
values[92]: 138.0
values[93]: 104.0
values[94]: 135.0
values[95]: 196.0
values[96]: 144.0
values[97]: 60.0
values[98]: 250.0
values[99]: 190.0
values[100]: 232.0
values[101]: 116.0
values[102]: 109.0
values[103]: 47.0
values[104]: 229.0
values[105]: 165.0
values[106]: 37.0
values[107]: 141.0
values[108]: 253.0
values[109]: 224.0
values[110]: 142.0
values[111]: 240.0
values[112]: 144.0
values[113]: 35.0
values[114]: 241.0
values[115]: 178.0
values[116]: 92.0
values[117]: 245.0
values[118]: 149.0
values[119]: 147.0
values[120]: 52.0
values[121]: 119.0
values[122]: 15.0
values[123]: 190.0
values[124]: 224.0
values[125]: 150.0
values[126]: 130.0
values[127]: 112.0
values[128]: 210.0
values[129]: 125.0
values[130]: 46.0
values[131]: 186.0
values[132]: 241.0
values[133]: 155.0
values[134]: 233.0
values[135]: 214.0
values[136]: 64.0
values[137]: 15.0
values[138]: 99.0
values[139]: 62.0
values[140]: 239.0
values[141]: 242.0
values[142]: 46.0
values[143]: 128.0
values[144]: 21.0
values[145]: 31.0
values[146]: 50.0
values[147]: 113.0
values[148]: 21.0
values[149]: 199.0
values[150]: 5.0
values[151]: 73.0
values[152]: 63.0
values[153]: 20.0
values[154]: 7.0
values[155]: 31.0
values[156]: 170.0
values[157]: 137.0
values[158]: 143.0
values[159]: 124.0
values[160]: 6.0
values[161]: 189.0
values[162]: 54.0
values[163]: 248.0
values[164]: 88.0
values[165]: 32.0
values[166]: 206.0
values[167]: 153.0
values[168]: 47.0
values[169]: 50.0
values[170]: 215.0
values[171]: 30.0
values[172]: 36.0
values[173]: 5.0
values[174]: 158.0
values[175]: 57.0
values[176]: 37.0
values[177]: 209.0
values[178]: 171.0
values[179]: 58.0
values[180]: 152.0
values[181]: 176.0
values[182]: 131.0
values[183]: 215.0
values[184]: 196.0
values[185]: 138.0
values[186]: 246.0
values[187]: 110.0
values[188]: 19.0
values[189]: 133.0
values[190]: 234.0
values[191]: 26.0
values[192]: 66.0
values[193]: 32.0
values[194]: 18.0
values[195]: 155.0
values[196]: 64.0
values[197]: 224.0
values[198]: 52.0
values[199]: 111.0
values[200]: 18.0
values[201]: 11.0
values[202]: 142.0
values[203]: 54.0
values[204]: 16.0
values[205]: 44.0
values[206]: 112.0
values[207]: 53.0
values[208]: 253.0
values[209]: 27.0
values[210]: 111.0
values[211]: 150.0
values[212]: 203.0
values[213]: 242.0
values[214]: 109.0
values[215]: 143.0
values[216]: 124.0
values[217]: 100.0
values[218]: 253.0
values[219]: 144.0
values[220]: 233.0
values[221]: 231.0
values[222]: 170.0
values[223]: 44.0
values[224]: 7.0
values[225]: 188.0
values[226]: 199.0
values[227]: 72.0
values[228]: 156.0
values[229]: 251.0
values[230]: 183.0
values[231]: 175.0
values[232]: 6.0
values[233]: 69.0
values[234]: 229.0
values[235]: 22.0
values[236]: 114.0
values[237]: 85.0
values[238]: 76.0
values[239]: 111.0
values[240]: 112.0
values[241]: 187.0
values[242]: 5.0
values[243]: 59.0
values[244]: 174.0
values[245]: 115.0
values[246]: 202.0
values[247]: 42.0
values[248]: 215.0
values[249]: 199.0
values[250]: 186.0
values[251]: 192.0
values[252]: 174.0
values[253]: 100.0
values[254]: 236.0
values[255]: 182.0
"""
