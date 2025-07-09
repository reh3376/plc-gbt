
            // Create PID-specific relationship types
            // Relationships will be created as data is inserted
            
            // MANIPULATES: ControlVariable -> ProcessVariable
            // DISTURBS: DisturbanceVariable -> ProcessVariable  
            // FEEDS_SP_OF: PIDLoop -> PIDLoop (cascade)
            // CASCADES_TO: PIDLoop -> PIDLoop
            // CONTROLS: PIDController -> PIDLoop
            // HAS_PV: PIDLoop -> ProcessVariable
            // HAS_CV: PIDLoop -> ControlVariable
            // HAS_DV: PIDLoop -> DisturbanceVariable
            