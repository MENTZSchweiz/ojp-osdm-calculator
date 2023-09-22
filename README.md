# ojp-osdm-calculator

This tool uses OJP and OSDM to get Fare information for a trip.

1. It gets the Trip information from OJP
2. Then it parses the OSDM Data
3. searches for the trip segments inside the osdm data to get fare information
4. Adds up all fares from the single segments
5. prints out all the trips with direct fare and the calculated fare:

**Following trips were found from Bern to Luzern via Langnau i.E.**:
- **For Trip 1** starting at 2023-09-22T07:42:00Z and ending at 2023-09-22T09:43:00Z the direct fare is 0 and the calculated fare is 4020
    - The leg 1 from Bern to Langnau i.E. has a fare of 1740
    - The leg 2 from Langnau i.E. to Luzern has a fare of 2280

- **For Trip 2** starting at 2023-09-22T08:36:00Z and ending at 2023-09-22T10:03:00Z the direct fare is 0 and the calculated fare is 3900
    - The leg 1 from Bern to Luzern has a fare of 3900

- **For Trip 3** starting at 2023-09-22T08:42:00Z and ending at 2023-09-22T10:43:00Z the direct fare is 0 and the calculated fare is 4020
    - The leg 1 from Bern to Langnau i.E. has a fare of 1740
    - The leg 2 from Langnau i.E. to Luzern has a fare of 2280

- **For Trip 4** starting at 2023-09-22T09:36:00Z and ending at 2023-09-22T11:03:00Z the direct fare is 0 and the calculated fare is 3900
    - The leg 1 from Bern to Luzern has a fare of 3900

- **For Trip 5** starting at 2023-09-22T09:42:00Z and ending at 2023-09-22T11:43:00Z the direct fare is 0 and the calculated fare is 4020
    - The leg 1 from Bern to Langnau i.E. has a fare of 1740
    - The leg 2 from Langnau i.E. to Luzern has a fare of 2280

## How to use this tool

1. clone the repository
2. download the osdm file from [this link](https://opentransportdata.swiss/de/dataset/osdm-offline)
3. put the osdm file in the repository, I only tested my script with the osdm version 10.7, so please use the file `osdm_ delivery_10_7.json`
4. Use following configuration in the python script:

```python
locationStart = "Bern"
locationEnd = "Luzern"
viaPointlocation = "Langnau"

# Either use BASIC (2nd class) or HIGH (1st class)
serviceClassRef = "BASIC"
# Either use YOUNG_CHILD, PRM_CHILD, CHILD or ADULT
passengerConstraint = "ADULT"
# Either use HALBTAX_CONSTRAINT, or None  
reductionConstraintRef = None
