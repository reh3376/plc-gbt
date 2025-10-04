Silo Volume and Weight Comparison Table
Overview
This table compares the key characteristics and performance metrics of four different silo geometries used in grain storage applications. All calculations are based on Python 2.7/Jython compatible scripts for industrial automation systems.

📊 SILO GEOMETRY COMPARISON
Parameter	            Silo1	Silo3	Silo4	Silo60	Units
Total Height	        35.984	35.984	35.984	6.213	ft
Cone Height	            10.516	5.875	9.984	1.885	ft
Cylinder Height	        25.469	30.109	26.000	4.328	ft
Cone Bottom Radius	    0.563	0.563	0.563	0.354	ft
Cone Top Radius	        10.734	6.154	6.154	1.990	ft
Cylinder Diameter	    21.536	12.307	12.307	3.979	ft
Cylinder Cross-Section	364.28	118.89	118.89	12.46	ft²
🎯 OPERATIONAL PARAMETERS
Parameter	            Silo1	Silo3	Silo4	Silo60	Units
Dead Volume Height	    3.150	4.350	3.924	0.100	ft
Safety Factor Height	3.000	2.500	2.500	1.100	ft
Usable Height Range	    29.834	29.134	29.560	5.014	ft
📈 VOLUME CAPACITY METRICS
Parameter	                Silo1	Silo3	Silo4	Silo60	Units
Total Capacity (100%)	    9,525.07	3,541.98	3,232.32	50.22	ft³
Volume at 0%	50.72	    114.22	40.23	0.05	ft³
P_percent when cone full	24.69%	5.23%	20.50%	35.61%	%
Volume when cone full	    1,340.10	257.46	436.68	10.08	ft³
Cylinder volume only	    8,184.98	3,284.52	2,795.65	40.14	ft³
ft³ per 1% in cylinder	    108.68	34.66	35.17	0.62	ft³/%
🌾 GRAIN STORAGE CAPACITY
Based on 56 lb/bushel corn density.

Parameter	                Silo1	Silo3	Silo4	Silo60	Units
Maximum Weight	            428,628	159,389	145,455	2,260	lb
Maximum Bushels	            7,654	2,846	2,597	40	bushels
Bushels per 1% (cylinder)	87.3	27.9	28.3	0.5	bu/%
🔍 PERFORMANCE CHARACTERISTICS
Cone Filling Behavior
Silo3: Fastest cone fill (5.23% to reach cylinder)
Silo4: Medium cone fill (20.50% to reach cylinder)
Silo1: Medium cone fill (24.69% to reach cylinder)
Silo60: Slowest cone fill (35.61% to reach cylinder)
Cylindrical Section Efficiency
Silo1: Highest rate (108.68 ft³ per 1% level change)
Silo3: Medium rate (34.66 ft³ per 1% level change)
Silo4: Medium rate (35.17 ft³ per 1% level change)
Silo60: Lowest rate (0.62 ft³ per 1% level change)
Volume Ratios (vs Silo1)
Silo3: 37.2% of Silo1 capacity
Silo4: 34.0% of Silo1 capacity
Silo60: 0.5% of Silo1 capacity
💡 APPLICATION RECOMMENDATIONS
Silo1 - Large Commercial Storage
Best for: High-volume grain handling operations
Capacity: 7,654 bushels (428,628 lb)
Characteristics: Largest diameter, highest throughput efficiency
Silo3 - Medium Commercial Storage
Best for: Medium-scale operations with space constraints
Capacity: 2,846 bushels (159,389 lb)
Characteristics: Shorter cone, better headspace management
Silo4 - Medium Commercial Storage (Conservative)
Best for: Medium-scale operations requiring conservative design
Capacity: 2,597 bushels (145,455 lb)
Characteristics: Taller cone, most conservative usable volume
Silo60 - Laboratory/Small-Scale
Best for: Laboratory testing, small-scale applications
Capacity: 40 bushels (2,260 lb)
Characteristics: Compact design, precise measurement capability
📋 SCRIPT INFORMATION
Silo Type	Script Location	Status	Python Compatibility
Silo1	scripts/Silo1-vol-weight.py	✅ Active	Python 2.7/Jython
Silo3	scripts/Silo3-vol-weight.py	✅ Active	Python 2.7/Jython
Silo4	scripts/silo4-vol-weight.py	✅ Active	Python 2.7/Jython
Silo60	scripts/docs/silo60-vol-weight.py	✅ Active	Python 2.7/Jython
🔧 USAGE NOTES
Level Transmitter Range: All scripts assume 0-102.25% level transmitter input (extended range)
Volume Calculations: Use piecewise cone + cylinder geometry
Weight Calculations: Support any grain density in lb/bushel
Industrial Compatibility: All scripts compatible with Jython automation systems
Validation: Silo1 script validated against reference CSV data
