<!-- LTeX: language=en-EN -->
# 🔩 Hardware At Hand

**Magpro TUB00154-SA-W06:**

* XRF and X-ray imaging
* 60kV (70 keV?)
* Spot size (.25 x 1.07)mm
* ~17.6e3cps @ 16.4uA (40kV)

**SA** => SPI (**S**) and Analog (**A**) control type

**W06** => Tungsten target (transmition lines provided by [NIST](https://physics.nist.gov/cgi-bin/XrayTrans/search.pl?element=W&lower=&upper=&units=eV))

Made by [Moxtec](https://moxtek.com/) and distributed (EU) by [Quantum Design](https://qd-europe.com/de/de/)

## 📜 Documentation

Available documentation can be found inside this repo:

* [DATASHEET_TUB00154-SA-W06.pdf](docs\OnPaper\DATASHEET_TUB00154-SA-W06\DATASHEET_TUB00154-SA-W06.pdf)
* [MANUAL_TUB-MAN-1007.pdf](docs\OnPaper\MANUAL_TUB-MAN-1007\MANUAL_TUB-MAN-1007.pdf)

and on my OneDrive:

* []()
* []()

# 👀 Stuff to do

In no particular order:

* [ ] Text *[Quantum Design](https://qd-europe.com/de/de/)* about
  * [x] Linux-Software available?
  
    >*No, only Microsoft*

    * [ ] Make custom software?
  * [x] how to switch analog <=> digital control

    >*"10-pin is programmed for either I2C, SPI or Analog at the factory.  If a customer orders with Analog, they need to run digital through the USB or send back for reprograming and testing."*

  * [x] further documentation

    >*"FYI, 12W can operate down to -5kV setting, but the spec docs currently talk to the settings for 40kV and above.  If the customer wants to operate below 40kV, the voltage is scaled linearly from 0-4.667VDC for 0 to -70kV(but will not run at all at voltages less than -4kV setting), and 0-4VDC for 0 to 1000uA current setting.  Current needs to be limited to not exceed 12W total power, so 1,000uA does not work well above 12kV setting, and they will need to reduce the emission current as they select higher kV to keep power at or below 12W.  -W06 target is really not meant to be run below 40kV, as the W coating is thick enough that it blocks a majority of the flux intensity at kV settings below 30kV.  They can run down as low as 30kV, but stability may be affected in their application below 40kV setting."*

    Additional spec sheet and drawings are made available 👌 but are classified. => Plz check [OneDrive](https://hsrheinmain-my.sharepoint.com/:f:/g/personal/lmy9f42u92_hsrheinmain_onmicrosoft_com/Eu1u_OxAc6tNtfoioA8n_JEBt5x4kzV99mTDH0zqPgQLmQ?email=daniel.muenstermann%40hs-rm.de&e=uNh9up).
  * [ ] CAD files
* [ ] Enclosure options
  * [ ] [Zarges-Boxes](https://www.zarges.com/de/produkte/verpacken-transportieren/kisten)?
  * [ ] Interior modification?
* [ ] Interlock
* [ ] Pb-Shielding
  * [ ] Make measurements
  * [ ] Find distributor => pre-order
* [ ] Make CAD-Model