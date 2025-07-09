
            // Insert sample PID loop data
            CREATE (loop:PIDLoop {
                loop_id: 'REACTOR_TEMP_LOOP',
                name: 'Reactor Temperature Control Loop',
                description: 'Primary temperature control for chemical reactor',
                process_type: 'Temperature',
                multi_pv_strategy: 'primary',
                created_at: datetime(),
                updated_at: datetime()
            })
            
            CREATE (controller:PIDController {
                controller_id: 'TEMP_PID_001',
                name: 'Reactor Temperature Controller',
                pid_loop_id: 'REACTOR_TEMP_LOOP',
                kc: 2.5,
                ti: 5.0,
                td: 1.0,
                algorithm_form: 'Independent',
                instruction_type: 'PIDE',
                control_mode: 'PID',
                update_period: 0.5
            })
            
            CREATE (pv:ProcessVariable {
                tag_name: 'ReactorTemp_PV',
                name: 'Reactor Temperature',
                engineering_units: '°C',
                operating_range_min: 20.0,
                operating_range_max: 200.0,
                opc_ua_address: 'ns=2;s=ReactorSystem.Temperature.PV',
                is_primary: true,
                weight: 1.0
            })
            
            CREATE (cv:ControlVariable {
                tag_name: 'HeaterOutput_CV',
                name: 'Heater Output',
                engineering_units: '%',
                output_range_min: 0.0,
                output_range_max: 100.0,
                opc_ua_address: 'ns=2;s=ReactorSystem.Heater.Output'
            })
            
            CREATE (dv:DisturbanceVariable {
                tag_name: 'AmbientTemp_DV',
                name: 'Ambient Temperature',
                engineering_units: '°C',
                opc_ua_address: 'ns=2;s=ReactorSystem.Ambient.Temperature',
                effect_type: 'direct'
            })
            
            // Create relationships
            CREATE (controller)-[:CONTROLS]->(loop)
            CREATE (loop)-[:HAS_PV]->(pv)
            CREATE (loop)-[:HAS_CV]->(cv)
            CREATE (loop)-[:HAS_DV]->(dv)
            CREATE (cv)-[:MANIPULATES]->(pv)
            CREATE (dv)-[:DISTURBS]->(pv)
            