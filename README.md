<p align="center" width="100%">
    <img  src="https://github.com/user-attachments/assets/11b077e9-37bf-4cea-b013-27f50b4467c4">
</p>
<!-- ![SSDC Logo](https://github.com/user-attachments/assets/11b077e9-37bf-4cea-b013-27f50b4467c4) -->

This is the Ground Control Station (GCS) codebase for the University of Florida's Space Systems Design Club (SSDC) CanSat team under Yoni Gutmann and Ashlee Rice-Bladykas.

Many of the files here serve no purpose and may or may not be removed at some point (hopefully). There are two files of importance, `gui.py` and `GCSXbee.py`, as well as the `Images` folder. Ensure that at least these files are present if not the whole repo.

At `line 14 of gui.py` there is a variable for the MAC address of the radio that will be on the mainboard on the Can, take great care to ensure that this is correct or else the radios will not communicate at all on the GCS end. Similarly, at `line 13 of GCSXbee.py` there is another string that holds the file path to the simulation data csv provided by the competition should it be required. On `line 31 of gui.py`, the file path for the csv of the collected data is defined. Only the drive letter should need to be changed in this case.

For debugging purposes, there is a rudimentary command line debugger that should hopefully aid in any issues arise.

If everything is configured properly you only need to run `gui.py` since this acts as the main for the GCS. If the UI is not displaying any data, check first that there are no errors on the terminal and if there are none, double check the MAC address of the radio. Good luck! :+1:

<p align="center" width="100%">
  <img width="33%" src="https://github.com/user-attachments/assets/9cc3b714-5c17-4917-aa7a-ec1373fa5680">
</p>
<!-- ![Gators Logo](https://github.com/user-attachments/assets/9cc3b714-5c17-4917-aa7a-ec1373fa5680) -->
