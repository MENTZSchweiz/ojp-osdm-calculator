import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from typing import List
from dataclasses import dataclass
from typing import List, Optional



# Redefine the Trip class to better handle cases where certain attributes might be missing

class Trip:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.leg_details = []

    def __repr__(self):
        return f"Trip(start_time={self.start_time}, end_time={self.end_time}, leg_details={self.leg_details}, journey_ref={self.journey_ref}, line_ref={self.line_ref}, published_line_name={self.published_line_name})"

class LegDetail:
    def __init__(self):
        self.timedLeg = None
        self.board_elem = None
        self.alight_elem = None
        self.text_board_elem = None
        self.text_alight_elem = None
        self.intermediate_legs = []  # Initialize the inner list for SubDetail objects
        self.journey_ref_elem = None
        self.line_ref_elem = None
        self.published_name_elem = None
        
class LegIntermediate:
    def __init__(self):
        self.stoppointref = None
        self.text = None
        # Add other attributes as needed

class LegsFare:
    def __init__(self):
        self.startText:str = None
        self.endText:str = None
        self.fare:int = None

class TripFare:
    def __init__(self):
        self.startText:str = None
        self.endText:str = None
        self.directFare:int = 0
        self.calculatedFare:int = 0
        self.legsFare = []
        self.nolegsNeeded:bool = None
        self.startTime:str = None
        self.endTime:str = None

class TripsFare:
    def __init__(self):
        self.trips = []

# Define the data classes
@dataclass
class subPrice:
    currency: str
    amount: int
    scale: int

@dataclass
class Price:
    id: str
    price: List[subPrice]

# Define updated data classes
@dataclass
class Station:
    codeList: str
    code: str
    country: str

@dataclass
class Route:
    isBorder: bool
    station: Station

@dataclass
class ViaStations:
    isBorder: bool
    carrierConstraintRef: str
    route: List[Route]

@dataclass
class RegionalValidity:
    seqNb: int
    viaStations: ViaStations

@dataclass
class RegionalConstraint:
    id: str
    entryConnectionPointId: str
    exitConnectionPointId: str
    regionalValidity: List[RegionalValidity]
    distance: int

@dataclass
class Fare:
    def __init__(self, id: str, bundleRef: str, fareType: str, priceRef: str, regionalConstraintRef: str, carrierConstraintRef: str, regulatoryConditions: List[str], serviceClassRef: str, passengerConstraintRef: str, legacyAccountingIdentifier: dict, reductionConstraintRef: str = None, legacyConversion:str = None, individualContracts:str = None, nameRef:str = None):
        self.id = id
        self.bundleRef = bundleRef
        self.fareType = fareType
        self.nameRef = nameRef
        self.priceRef = priceRef
        self.regionalConstraintRef = regionalConstraintRef
        self.carrierConstraintRef = carrierConstraintRef
        self.regulatoryConditions = regulatoryConditions
        self.serviceClassRef = serviceClassRef
        self.passengerConstraintRef = passengerConstraintRef
        self.legacyAccountingIdentifier = legacyAccountingIdentifier
        self.reductionConstraintRef = reductionConstraintRef
        self.legacyConversion = legacyConversion
        self.individualContracts = individualContracts

class StopPointInformation:
    stopPointRef: str
    stopPointText: str

def getStopPlaceRefFromLocation(location,  dep_arr_time=None):
    url = "https://odpch-api.clients.liip.ch/ojp-int-linux"
    headers = {
        "Content-Type": "text/xml",
        "Authorization": "Bearer eyJvcmciOiI2M2Q4ODhiMDNmZmRmODAwMDEzMDIwODkiLCJpZCI6IjZkYzViNTFjNjFlNzQyY2E4YjNhYzQ0YzQyZGY0MTY1IiwiaCI6Im11cm11cjEyOCJ9"
    }

    # If dep_arr_time is not given, use the current time
    if not dep_arr_time:
        dep_arr_time = datetime.utcnow().isoformat() + "Z"

    data = f"""<?xml version="1.0" encoding="utf-8"?>
                <OJP xmlns="http://www.siri.org.uk/siri" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ojp="http://www.vdv.de/ojp" xsi:schemaLocation="http://www.siri.org.uk/siri ../ojp-xsd-v1.0/OJP.xsd" version="1.0">
                <OJPRequest>
                    <ServiceRequest>
                    <RequestorRef>OJP SDK v1.0</RequestorRef>
                    <RequestTimestamp>{dep_arr_time}</RequestTimestamp>
                    <ojp:OJPLocationInformationRequest>
                        <RequestTimestamp>{dep_arr_time}</RequestTimestamp>
                        <ojp:InitialInput>
                        <ojp:LocationName>{location}</ojp:LocationName>
                        </ojp:InitialInput>
                        <ojp:Restrictions>
                        <ojp:NumberOfResults>1</ojp:NumberOfResults>
                        </ojp:Restrictions>
                        <Extensions>
                        <ParamsExtension>
                            <PrivateModeFilter>
                            <Exclude>false</Exclude>
                            </PrivateModeFilter>
                        </ParamsExtension>
                        </Extensions>
                    </ojp:OJPLocationInformationRequest>
                    </ServiceRequest>
                </OJPRequest>
                </OJP>"""



    response = requests.post(url, headers=headers, data=data)
    ET.register_namespace('siri',"http://www.siri.org.uk/siri") #some name
    ET.register_namespace('ojp',"http://www.vdv.de/ojp") #some name
    tree = ET.ElementTree(ET.fromstring(response.text))
    stopPointInformation = StopPointInformation() 
    stopPointInformation.stopPointRef = tree.find('.//{http://www.vdv.de/ojp}StopPlaceRef').text
    stopPointInformation.stopPointText = tree.find('.//{http://www.vdv.de/ojp}StopPlaceName/{http://www.vdv.de/ojp}Text').text
    return stopPointInformation

def send_request(originStopPointInformation, destinationStopPointInformation,  viaStopPointInformation=None,  dep_arr_time=None):
    url = "https://odpch-api.clients.liip.ch/ojp-int-linux"
    headers = {
        "Content-Type": "text/xml",
        "Authorization": "Bearer eyJvcmciOiI2M2Q4ODhiMDNmZmRmODAwMDEzMDIwODkiLCJpZCI6IjZkYzViNTFjNjFlNzQyY2E4YjNhYzQ0YzQyZGY0MTY1IiwiaCI6Im11cm11cjEyOCJ9"
    }

    # If dep_arr_time is not given, use the current time
    if not dep_arr_time:
        dep_arr_time = datetime.utcnow().isoformat() + "Z"

        via_point = ""
        if viaStopPointInformation is not None: 
            via_point = f"""<ojp:Via>
                        <ojp:ViaPoint>
                            <StopPointRef>{viaStopPointInformation.stopPointRef}</StopPointRef>
                            <ojp:LocationName>
                                <ojp:Text>{viaStopPointInformation.stopPointText}</ojp:Text>
                            </ojp:LocationName>
                        </ojp:ViaPoint>
                    </ojp:Via>"""
    
    
    data = f"""<?xml version="1.0" encoding="UTF-8"?>
                <OJP xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.siri.org.uk/siri" version="1.0" xmlns:ojp="http://www.vdv.de/ojp" xsi:schemaLocation="http://www.siri.org.uk/siri ../ojp-xsd-v1.0/OJP.xsd">
                    <OJPRequest>
                        <ServiceRequest>
                            <RequestTimestamp>{dep_arr_time}</RequestTimestamp>
                            <RequestorRef>MENTZ-Postman-Test</RequestorRef>
                            <ojp:OJPTripRequest>
                                <RequestTimestamp>{dep_arr_time}</RequestTimestamp>
                                <MessageIdentifier>756</MessageIdentifier>
                                <ojp:Origin>
                                    <ojp:PlaceRef>
                                        <StopPointRef>{originStopPointInformation.stopPointRef}</StopPointRef>
                                        <ojp:LocationName>
                                            <ojp:Text>{originStopPointInformation.stopPointText}</ojp:Text>
                                        </ojp:LocationName>
                                    </ojp:PlaceRef>
                                    <ojp:DepArrTime>{dep_arr_time}</ojp:DepArrTime>
                                </ojp:Origin>
                                <ojp:Destination>
                                    <ojp:PlaceRef>
                                        <StopPointRef>{destinationStopPointInformation.stopPointRef}</StopPointRef>
                                        <ojp:LocationName>
                                            <ojp:Text>{destinationStopPointInformation.stopPointText}</ojp:Text>
                                        </ojp:LocationName>
                                    </ojp:PlaceRef>
                                </ojp:Destination>
                                """ + via_point + """<ojp:Params>
                                    <ojp:NumberOfResults>5</ojp:NumberOfResults>
                                    <ojp:IncludeIntermediateStops>true</ojp:IncludeIntermediateStops>
                                </ojp:Params>
                            </ojp:OJPTripRequest>
                        </ServiceRequest>
                    </OJPRequest>
                </OJP>"""



    response = requests.post(url, headers=headers, data=data)
    return response

def parse_xml_to_trips(response):
    # Parse the XML again
    trips = []
    ET.register_namespace('siri',"http://www.siri.org.uk/siri") #some name
    ET.register_namespace('ojp',"http://www.vdv.de/ojp") #some name
    tree = ET.ElementTree(ET.fromstring(response.text))
    trip_results = tree.findall('.//{http://www.vdv.de/ojp}TripResult')


    for trip_result in trip_results:
        trip = Trip()
        
        # Safely get start_time and end_time
        trip.start_time = trip_result.find(".//{http://www.vdv.de/ojp}StartTime").text
        trip.end_time = trip_result.find(".//{http://www.vdv.de/ojp}EndTime").text

        trip_legs = trip_result.findall(".//{http://www.vdv.de/ojp}TripLeg")
        
        for leg in trip_legs:
            leg_detail = LegDetail()
            
            # Safely get board_stop_point_ref, alight_stop_point_ref and text
            if(leg.find(".//{http://www.vdv.de/ojp}LegBoard") is not None):
                
                leg_detail.timedLeg = True
                            
                leg_detail.board_elem = leg.find(".//{http://www.vdv.de/ojp}LegBoard/{http://www.siri.org.uk/siri}StopPointRef").text
                leg_detail.alight_elem = leg.find(".//{http://www.vdv.de/ojp}LegAlight/{http://www.siri.org.uk/siri}StopPointRef").text
                leg_detail.text_board_elem = leg.find(".//{http://www.vdv.de/ojp}LegBoard/{http://www.vdv.de/ojp}StopPointName/{http://www.vdv.de/ojp}Text").text
                leg_detail.text_alight_elem = leg.find(".//{http://www.vdv.de/ojp}LegAlight/{http://www.vdv.de/ojp}StopPointName/{http://www.vdv.de/ojp}Text").text
                
                intermediates_legs = leg.findall(".//{http://www.vdv.de/ojp}LegIntermediates")
                
                for intermedia_leg in intermediates_legs:
                    intermediate_leg_detail = LegIntermediate()
                    
                    intermediate_leg_detail.stoppointref = intermedia_leg.find(".//{http://www.siri.org.uk/siri}StopPointRef").text
                    intermediate_leg_detail.text = intermedia_leg.find(".//{http://www.vdv.de/ojp}StopPointName/{http://www.vdv.de/ojp}Text").text
                
                    
                    leg_detail.intermediate_legs.append(intermediate_leg_detail)
                
                # Extract JourneyRef, LineRef and PublishedLineName for each leg safely
                service = leg.find(".//{http://www.vdv.de/ojp}Service")
                if service:
                    leg_detail.journey_ref_elem = service.find(".//{http://www.vdv.de/ojp}JourneyRef").text
                    leg_detail.line_ref_elem = service.find(".//{http://www.siri.org.uk/siri}LineRef").text
                    leg_detail.published_name_elem = service.find(".//{http://www.vdv.de/ojp}PublishedLineName/{http://www.vdv.de/ojp}Text").text
                
            if(leg.find(".//{http://www.vdv.de/ojp}LegStart") is not None):
                
                leg_detail.timedLeg = False
                
                leg_detail.board_elem = leg.find(".//{http://www.vdv.de/ojp}LegStart/{http://www.siri.org.uk/siri}StopPointRef").text
                leg_detail.alight_elem = leg.find(".//{http://www.vdv.de/ojp}LegEnd/{http://www.siri.org.uk/siri}StopPointRef").text
                leg_detail.text_board_elem = leg.find(".//{http://www.vdv.de/ojp}LegStart/{http://www.vdv.de/ojp}LocationName/{http://www.vdv.de/ojp}Text").text
                leg_detail.text_alight_elem = leg.find(".//{http://www.vdv.de/ojp}LegEnd/{http://www.vdv.de/ojp}LocationName/{http://www.vdv.de/ojp}Text").text

            trip.leg_details.append(leg_detail)

        trips.append(trip)

    return trips

def parse_json_file(filename: str):
    with open(filename, 'r') as file:
        osdm_data = json.load(file)
        
        # Deserialize the specified sections
        regional_constraints = [RegionalConstraint(**rc) for rc in osdm_data['fareDelivery']['fareStructure']['regionalConstraints']]
        prices = [Price(**p) for p in osdm_data['fareDelivery']['fareStructure']['prices']]
        fares = [Fare(**f) for f in osdm_data['fareDelivery']['fareStructure']['fares']]
        
        return fares, regional_constraints, prices

def search_for_regional_constraint(regional_constraints: List[RegionalConstraint], 
                                   entry_id: str, 
                                   exit_id: str) -> Optional[RegionalConstraint]:
    """
    Search for a RegionalConstraint with a specific entryConnectionPointId and exitConnectionPointId within a given list.
    
    Parameters:
    - regional_constraints: the list of RegionalConstraint objects.
    - entry_id: the entryConnectionPointId to search for.
    - exit_id: the exitConnectionPointId to search for.

    Returns:
    - The found RegionalConstraint object or None if not found.
    """
    foundConstraints = []
    
    for rc in regional_constraints:
        if rc.entryConnectionPointId == entry_id and rc.exitConnectionPointId == exit_id:
            foundConstraints.append(rc)
    return foundConstraints

def search_for_fare(fares: List[Fare], 
                   regionalConstraintRef: str,
                   passengerConstraintRef: str,
                   serviceClassRef,
                   reductionConstraintRef: Optional[str] = None) -> Optional[Fare]:
    """
    Search for a Fare with a specific regionalConstraintRef, passengerConstraintRef, and reductionConstraintRef within a given list.
    
    Parameters:
    - fares: the list of Fare objects.
    - regionalConstraintRef: the regionalConstraintRef to search for.
    - passengerConstraintRef: the passengerConstraintRef to search for.
    - reductionConstraintRef: the reductionConstraintRef to search for.

    Returns:
    - The found Fare object or None if not found.
    """
    for fare in fares:
        if fare.regionalConstraintRef == regionalConstraintRef and fare.passengerConstraintRef == passengerConstraintRef and fare.serviceClassRef == serviceClassRef:
            if fare.reductionConstraintRef == reductionConstraintRef:
                return fare
            if fare.reductionConstraintRef is None and reductionConstraintRef is None:
                return fare
    return None

def get_amount(prices: List[Price], 
                                   id: str) -> Optional[Fare]:
    """
    Search for a RegionalConstraint with a specific entryConnectionPointId and exitConnectionPointId within a given list.
    
    Parameters:
    - regional_constraints: the list of RegionalConstraint objects.
    - entry_id: the entryConnectionPointId to search for.
    - exit_id: the exitConnectionPointId to search for.

    Returns:
    - The found RegionalConstraint object or None if not found.
    """
    for price in prices:
        if price.id == id:
            return price
    return None

def validate_regionalConstraint(regionalConstraint, leg):
    for regionalValidity in regionalConstraint.regionalValidity:
        for route in regionalValidity['viaStations']['route']:               
            foundIntermediateLegInRoute = False
            if 'station' in route:
                routePoint = route['station']['code']
            if 'alternativeRoute' in route:
                routePoint = route['alternativeRoute'][0]['station']['code']
                routePoint = routePoint+route['alternativeRoute'][1]['station']['code']
            for intemediate_leg in leg.intermediate_legs:
                if intemediate_leg.stoppointref in routePoint or leg.board_elem in routePoint or leg.alight_elem in routePoint:
                    foundIntermediateLegInRoute = True
            if foundIntermediateLegInRoute is not True:
                return False
        return True


def calculate_trips_fare(trips, regionalConstraints, fares, prices, tripStart, tripEnd, passengerConstraint, reductionConstraintRef, serviceClassRef):
    tripsFare = TripsFare()

    for trip in trips:
        tripFare = TripFare()
        tripFare.startTime = trip.start_time
        tripFare.endTime = trip.end_time
        # search for fare price from beginning to end
        # foundConstraints = search_for_regional_constraint(regionalConstraints, tripStart.stopPointRef, tripEnd.stopPointRef)
        # for regionalConstraint in foundConstraints:
        #     fare = search_for_fare(fares, regionalConstraint.id, passengerConstraint, serviceClassRef, reductionConstraintRef)
        #     price = get_amount(prices, fare.priceRef)
        #     tripFare.nolegsNeeded = True
        #     tripFare.directFare = price.price[0]["amount"]
        # else:
        #     tripFare.nolegsNeeded = False
        
        # search for calculated fare price through the legs
        for leg in trip.leg_details:
            if leg.timedLeg == True:
                legsFare = LegsFare()
                legsFare.startText = leg.text_board_elem
                legsFare.endText = leg.text_alight_elem
                
                # search for fare price from beginning to end of leg
                foundConstraints = search_for_regional_constraint(regionalConstraints, leg.board_elem, leg.alight_elem)
                legsFare.fare = 0
                for regionalConstraint in foundConstraints:
                    if validate_regionalConstraint(regionalConstraint, leg):      
                        fare = search_for_fare(fares, regionalConstraint.id, passengerConstraint, serviceClassRef, reductionConstraintRef)
                        price = get_amount(prices, fare.priceRef)
                        if price.price[0]["amount"] is not None:
                            legsFare.fare = price.price[0]["amount"]
                            break
                tripFare.calculatedFare += legsFare.fare
                tripFare.legsFare.append(legsFare)
                tripsFare.trips.append(tripFare)
    return tripsFare

def print_trip_details(tripsFare):        
    tripNumberIndex = 1
    for trip in tripsFare.trips:
        print(f"For Trip {tripNumberIndex} starting at {trip.startTime} and ending at {trip.endTime}, the calculated fare is {trip.calculatedFare}")
        tripNumberIndex+=1
        legFareIndex = 1
        for legFare in trip.legsFare:
            print(f"\tThe leg {legFareIndex} from {legFare.startText} to {legFare.endText} has a fare of {legFare.fare}")
            legFareIndex+=1

# -------------------------------------------------------------------------------------------------------------------------

locationStart = "Bern"
locationEnd = "Luzern"
viaPointlocation = "Langnau"

#Either use BASIC (2nd class) or HIGH (1st class)
serviceClassRef = "BASIC"
#Either use YOUNG_CHILD, PRM_CHILD, CHILD or ADULT
passengerConstraint = "ADULT"
#Either use HALBTAX_CONSTRAINT, or None  
reductionConstraintRef = None

#get didok
tripStart = getStopPlaceRefFromLocation(locationStart)
tripEnd = getStopPlaceRefFromLocation(locationEnd)
viaPoint = None
if viaPointlocation is not None:
    viaPoint = getStopPlaceRefFromLocation(viaPointlocation)
#getTrips
response = send_request(tripStart, tripEnd, viaPoint)
trips = parse_xml_to_trips(response)
#parse fares
fares, regionalConstraints, prices = parse_json_file("osdm_delivery_10_7.json")
# get fares from trip
tripsFare = calculate_trips_fare(trips, regionalConstraints, fares, prices, tripStart, tripEnd, passengerConstraint, reductionConstraintRef, serviceClassRef)
print(f"Following trips were found from {tripStart.stopPointText} to {tripEnd.stopPointText}" + (f" via {viaPoint.stopPointText}" if viaPoint else ""))
print_trip_details(tripsFare)

        

                
        











