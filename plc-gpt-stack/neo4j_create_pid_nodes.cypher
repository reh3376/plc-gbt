
            // Create PID-specific node types
            CREATE CONSTRAINT pid_loop_id IF NOT EXISTS FOR (p:PIDLoop) REQUIRE p.loop_id IS UNIQUE;
            CREATE CONSTRAINT pid_controller_id IF NOT EXISTS FOR (c:PIDController) REQUIRE c.controller_id IS UNIQUE;
            CREATE CONSTRAINT process_variable_tag IF NOT EXISTS FOR (pv:ProcessVariable) REQUIRE pv.tag_name IS UNIQUE;
            CREATE CONSTRAINT control_variable_tag IF NOT EXISTS FOR (cv:ControlVariable) REQUIRE cv.tag_name IS UNIQUE;
            CREATE CONSTRAINT disturbance_variable_tag IF NOT EXISTS FOR (dv:DisturbanceVariable) REQUIRE dv.tag_name IS UNIQUE;
            