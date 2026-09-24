"""Rule-based car problem data. Each yes/no answer adds a point to a likely cause."""

CAR_KEYWORDS = [
    " car ", " cars ", "vehicle", "engine", "brake", "tyre", "tire", "wheel", "battery", "oil", "clutch",
    "gear", "steering", "suspension", "exhaust", "radiator", "coolant", " ac ", "a/c", "aircon",
    "mileage", "fuel", "petrol", "diesel", "spark", "plug", "starter", "alternator", "horn",
    "headlight", "indicator", "dashboard", "warning light", "check engine", "smoke", "leak",
    "noise", "sound", "vibration", "overheat", "service", "mechanic", "repair", "garage",
    "transmission", "axle", "belt", "filter", "wiper", "sedan", " suv", "hatchback",
    "rpm", "idle", "stall", "accelerat", "pickup", "honda", "maruti", "hyundai", "toyota",
    "tata", "mahindra", "kia", "ford", "bmw", "audi", "swift", "creta", "nexon",
]

GREETINGS = {"hi", "hello", "hey", "hii", "namaste", "good morning", "good evening", "good afternoon"}
YES_WORDS = {"yes", "y", "yeah", "yep", "yup", "haan", "ha", "sure", "correct", "right", "true", "ok", "okay"}
NO_WORDS = {"no", "n", "nope", "nah", "nahi", "never", "false"}
BOOK_WORDS = {"book", "schedule", "appointment", "send mechanic", "agree"}

ISSUES = {
    "no_start": {
        "title": "Car not starting",
        "keywords": ["not start", "won't start", "wont start", "doesn't start", "does not start",
                     "not starting", "no start", "dead battery", "battery dead", "clicking", "crank"],
        "questions": [
            {"text": "When you turn the key, do you hear a fast clicking sound?", "yes": "battery", "no": "starter"},
            {"text": "Are the dashboard lights and headlights dim or not turning on?", "yes": "battery", "no": "fuel"},
            {"text": "Does the engine turn over (crank) but not fire up?", "yes": "fuel", "no": "starter"},
        ],
        "causes": {
            "battery": {
                "problem": "Weak or dead battery",
                "details": "Clicking sound and dim lights mean the battery cannot give enough power to the starter.",
                "recommendation": "Jump-start the car and get a battery health test. Replace the battery if it is older than 3-4 years.",
                "service": "Battery Check & Replacement",
                "urgency": "medium",
                "estimated_cost": "₹3,000 - ₹8,000",
            },
            "starter": {
                "problem": "Faulty starter motor or ignition switch",
                "details": "Power is available but the engine does not crank, so the starter motor or ignition circuit is likely faulty.",
                "recommendation": "Get the starter motor, solenoid and ignition switch tested. Do not keep trying to start the car repeatedly.",
                "service": "Starter Motor Repair",
                "urgency": "medium",
                "estimated_cost": "₹2,500 - ₹7,000",
            },
            "fuel": {
                "problem": "Fuel supply or spark problem",
                "details": "Engine cranks but does not start, which usually means fuel is not reaching the engine or spark plugs are weak.",
                "recommendation": "Check fuel level, fuel pump, fuel filter and spark plugs.",
                "service": "Fuel System & Ignition Check",
                "urgency": "medium",
                "estimated_cost": "₹1,500 - ₹6,000",
            },
        },
    },
    "overheating": {
        "title": "Engine overheating",
        "keywords": ["overheat", "over heat", "temperature high", "temperature gauge", "coolant", "radiator",
                     "steam", "boiling", "hot engine", "engine hot"],
        "questions": [
            {"text": "Is the coolant level below the minimum mark in the coolant tank?", "yes": "coolant_leak", "no": "fan"},
            {"text": "Do you see any green, pink or orange liquid leaking under the car?", "yes": "coolant_leak", "no": "thermostat"},
            {"text": "Does the temperature go up mostly when the car is standing still or in traffic?", "yes": "fan", "no": "thermostat"},
        ],
        "causes": {
            "coolant_leak": {
                "problem": "Coolant leak or low coolant",
                "details": "Low coolant and visible leaks point to a leaking radiator, hose or water pump.",
                "recommendation": "Stop driving when the gauge is high. Get the radiator, hoses and water pump checked for leaks and refill coolant.",
                "service": "Cooling System Leak Repair",
                "urgency": "high",
                "estimated_cost": "₹1,500 - ₹10,000",
            },
            "fan": {
                "problem": "Radiator fan not working",
                "details": "Heating up in traffic usually means the radiator fan is not pulling air when the car is not moving.",
                "recommendation": "Get the radiator fan motor, relay and fuse checked.",
                "service": "Radiator Fan Repair",
                "urgency": "high",
                "estimated_cost": "₹1,000 - ₹5,000",
            },
            "thermostat": {
                "problem": "Stuck thermostat or blocked radiator",
                "details": "Coolant is fine but not flowing properly, which usually means a stuck thermostat or clogged radiator.",
                "recommendation": "Replace the thermostat and flush the radiator.",
                "service": "Thermostat Replacement & Radiator Flush",
                "urgency": "high",
                "estimated_cost": "₹1,500 - ₹4,500",
            },
        },
    },
    "brakes": {
        "title": "Brake problem",
        "keywords": ["brake", "braking", "squeal", "squeak", "grinding"],
        "questions": [
            {"text": "Do you hear a squealing or squeaking sound when you press the brake?", "yes": "pads", "no": "fluid"},
            {"text": "Does the brake pedal feel soft or go down more than usual?", "yes": "fluid", "no": "pads"},
            {"text": "Does the steering or pedal shake (vibrate) when braking?", "yes": "rotors", "no": "pads"},
        ],
        "causes": {
            "pads": {
                "problem": "Worn brake pads",
                "details": "Squealing while braking is the wear indicator on brake pads.",
                "recommendation": "Replace the brake pads soon. Worn pads can damage the brake discs.",
                "service": "Brake Pad Replacement",
                "urgency": "high",
                "estimated_cost": "₹1,500 - ₹4,000",
            },
            "fluid": {
                "problem": "Low brake fluid or air in brake lines",
                "details": "A soft pedal means brake fluid is low, leaking, or there is air in the brake lines.",
                "recommendation": "Avoid driving. Get the brake fluid level and lines checked and bleed the brakes.",
                "service": "Brake Fluid & Line Service",
                "urgency": "high",
                "estimated_cost": "₹800 - ₹3,000",
            },
            "rotors": {
                "problem": "Warped brake discs (rotors)",
                "details": "Vibration while braking usually comes from uneven or warped brake discs.",
                "recommendation": "Get the brake discs resurfaced or replaced along with the pads.",
                "service": "Brake Disc Resurfacing / Replacement",
                "urgency": "medium",
                "estimated_cost": "₹2,500 - ₹8,000",
            },
        },
    },
    "check_engine": {
        "title": "Check engine light",
        "keywords": ["check engine", "engine light", "warning light", "malfunction light", "mil light", "engine symbol"],
        "questions": [
            {"text": "Is the check engine light blinking (flashing)?", "yes": "misfire", "no": "sensor"},
            {"text": "Does the engine shake or feel rough while idling?", "yes": "misfire", "no": "sensor"},
            {"text": "Did the light come on just after you filled fuel?", "yes": "fuel_cap", "no": "sensor"},
        ],
        "causes": {
            "misfire": {
                "problem": "Engine misfire",
                "details": "A blinking light and rough engine mean one or more cylinders are misfiring.",
                "recommendation": "Drive gently and get it checked quickly. Spark plugs, ignition coils or injectors may need replacement.",
                "service": "OBD Scan & Ignition Repair",
                "urgency": "high",
                "estimated_cost": "₹1,500 - ₹8,000",
            },
            "sensor": {
                "problem": "Faulty engine sensor (O2 / MAF sensor)",
                "details": "A steady light with normal driving usually means a sensor is giving wrong readings.",
                "recommendation": "Get an OBD scan to read the exact error code and replace the faulty sensor.",
                "service": "OBD Diagnostic Scan",
                "urgency": "low",
                "estimated_cost": "₹500 - ₹6,000",
            },
            "fuel_cap": {
                "problem": "Loose or faulty fuel cap",
                "details": "A loose fuel cap causes an evaporation leak, which turns on the light after refuelling.",
                "recommendation": "Tighten the fuel cap until it clicks. If the light stays on after 2-3 drives, get an OBD scan.",
                "service": "Fuel Cap Check & OBD Scan",
                "urgency": "low",
                "estimated_cost": "₹0 - ₹1,000",
            },
        },
    },
    "ac": {
        "title": "AC not cooling",
        "keywords": [ " ac ", "a/c", "air conditioner", "ac is not", "not cooling", "aircon", "ac cooling", "hot air"],
        "questions": [
            {"text": "Is the AC blowing air but the air is not cold?", "yes": "gas", "no": "blower"},
            {"text": "Is the air flow from the vents weak even at full fan speed?", "yes": "filter", "no": "gas"},
            {"text": "Do you hear a click from the engine area when you switch on the AC?", "yes": "gas", "no": "compressor"},
        ],
        "causes": {
            "gas": {
                "problem": "Low AC refrigerant gas",
                "details": "Air flows but is not cold, which usually means refrigerant gas is low due to a small leak.",
                "recommendation": "Get a leak test and AC gas refill.",
                "service": "AC Gas Refill & Leak Test",
                "urgency": "low",
                "estimated_cost": "₹1,500 - ₹3,500",
            },
            "filter": {
                "problem": "Blocked cabin air filter",
                "details": "Weak air flow at full speed usually means the cabin filter is full of dust.",
                "recommendation": "Replace the cabin air filter and clean the AC vents.",
                "service": "Cabin Filter Replacement",
                "urgency": "low",
                "estimated_cost": "₹400 - ₹1,200",
            },
            "blower": {
                "problem": "Blower motor or resistor fault",
                "details": "No air from vents means the blower motor or its resistor is not working.",
                "recommendation": "Get the blower motor, resistor and fuse checked.",
                "service": "AC Blower Repair",
                "urgency": "low",
                "estimated_cost": "₹1,000 - ₹4,000",
            },
            "compressor": {
                "problem": "AC compressor not engaging",
                "details": "No click from the compressor means the compressor clutch or its relay is faulty.",
                "recommendation": "Get the AC compressor, clutch and relay tested.",
                "service": "AC Compressor Repair",
                "urgency": "low",
                "estimated_cost": "₹3,000 - ₹15,000",
            },
        },
    },
    "engine_noise": {
        "title": "Strange engine noise",
        "keywords": ["knocking", "ticking", "rattling", "rattle", "whining", "engine noise", "engine sound",
                     "weird sound", "strange sound", "strange noise", "weird noise"],
        "questions": [
            {"text": "Is it a high-pitched squealing sound, mostly at startup or when you turn the AC on?", "yes": "belt", "no": "oil"},
            {"text": "Is it a ticking or knocking sound that gets faster as you press the accelerator?", "yes": "oil", "no": "exhaust"},
            {"text": "Is it a rattling sound that comes from under the car?", "yes": "exhaust", "no": "oil"},
        ],
        "causes": {
            "belt": {
                "problem": "Loose or worn drive belt",
                "details": "Squealing at startup or with AC load is a classic sign of a slipping drive belt.",
                "recommendation": "Get the drive belt and tensioner checked and replaced if cracked.",
                "service": "Drive Belt Replacement",
                "urgency": "medium",
                "estimated_cost": "₹800 - ₹3,000",
            },
            "oil": {
                "problem": "Low engine oil or worn engine parts",
                "details": "Ticking or knocking that follows engine speed often means low oil or poor lubrication.",
                "recommendation": "Check the oil level right away. Get an oil change and engine inspection.",
                "service": "Engine Oil Change & Inspection",
                "urgency": "high",
                "estimated_cost": "₹2,000 - ₹6,000",
            },
            "exhaust": {
                "problem": "Loose exhaust or heat shield",
                "details": "Rattling from under the car usually comes from a loose exhaust clamp or heat shield.",
                "recommendation": "Get the exhaust mounts, clamps and heat shield tightened or replaced.",
                "service": "Exhaust System Repair",
                "urgency": "low",
                "estimated_cost": "₹500 - ₹3,000",
            },
        },
    },
}
