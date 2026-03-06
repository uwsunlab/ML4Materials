# metadata
metadata = {
    "protocolName": "IMOD Protocol",
    "author": "Clara Tamura, Austin Martin",
    "description": "Mara OT-2 Protocol for IMOD project",
    "apiLevel": "2.19",
}

class OpentronMara:
    def __init__(self, protocol):
        self.protocol = protocol
        self.protocol._commands.clear()

        # Load tipracks
        self.tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '11')
        self.tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')

        # Load Pipettes
        self.pip20 = protocol.load_instrument('p20_single_gen2', mount='left', tip_racks=[self.tiprack_20])
        self.pip300 = protocol.load_instrument('p300_single_gen2', mount='right', tip_racks=[self.tiprack_300])

        # Track used tips manually
        self.tip_log = {
            self.pip300: {'tips': self.tiprack_300.wells(), 'next': 0},
            self.pip20: {'tips': self.tiprack_20.wells(), 'next': 0},
        }

        # Set pipette buffers
        self.pip20_buffer = 2
        self.pip300_buffer = 20
        self.pip20_threshold = 30

        # Set pipette transfer speeds
        self.pip20.flow_rate.aspirate = 10
        self.pip20.flow_rate.dispense = 10
        self.pip20.flow_rate.blow_out = 20

        self.pip300.flow_rate.aspirate = 50
        self.pip300.flow_rate.dispense = 50
        self.pip300.flow_rate.blow_out = 100

        # Load plates
        self.plate_96 = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', '8')
        self.plate_96.set_offset(x=0, y=0, z=2)  # Z lowered by 1 mm
    
        self.plate_24 = protocol.load_labware('corning_24_wellplate_3.4ml_flat','7')
        self.plate_24.set_offset(x=0, y=0, z=3)  # Z lowered by 1 mm
        self.source_wells = ['A1', 'B1', 'C1']

        # Load heater module
        self.hs_plate, self.hs_wells = self.set_custom_heater('3')
        # self.hs_mod, self.hs_plate, self.hs_wells = self.set_opentron_heater() # The opentron heater

        # Load the trash bin
        self.trash_bin = protocol.fixed_trash


        # Home the pipettes
        self.pip300.home()
        self.pip20.home()
    
        print("Initialization complete.")
    
    def set_opentron_heater(self, slot):
        # Load heater
        self.hs_mod = self.protocol.load_module("heaterShakerModuleV1", slot)
        self.hs_adapter = self.hs_mod.load_adapter("opentrons_universal_flat_adapter")
        self.hs_plate = self.hs_adapter.load_labware("corning_384_wellplate_112ul_flat")

        # heater offsets for dropcasting on to rectangle 12 samples
        self.hs_wells = {
            1: ('C4',  (-0.5, 1, 0)),
            2: ('C10', (-1.5, 1, 0)),
            3: ('C16', (-2.5, 1, 0)),
            4: ('C21', (1, 1, 0)),
            5: ('H4',  (0, -3, 0)),
            6: ('H10', (-1.5, -3, 0)),
            7: ('H16', (-2.5, -3, 0)),
            8: ('H21', (1.5, -3, 0)),
            9: ('N4',  (0, -1, 0)),
            10: ('N10', (-1, -1, 0)),
            11: ('N16', (-2.5, -1, 0)),
            12: ('N21', (1.5, -1, 0))
        }
        return self.hs_mod, self.hs_plate, self.hs_wells
    
    def set_custom_heater(self, slot):
        # heater offsets for dropcasting on to rectangle 12 samples
        # diameter o f96 = 7.0mm
        heater_plate = self.protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', slot)
        heater_plate.set_offset(x=-5, y=32, z=87) # Z lowered by 1 mm
        hs_offsets = {
            1: ('B2',  (-1.0,  +0.0 , -1.4)),
            2: ('B5',  (-1.0,  +0.0 , -1.4)),
            3: ('B8',  (-1.0,  +0.0 , -1.4)),
            4: ('B11', (-1.0,  +0.0 , -1.4)),
            5: ('E2',  (-1.0,  +0.0 , -1.4)),
            6: ('E5',  (-1.0,  +0.0 , -1.4)),
            7: ('E8',  (-1.0,  +0.0 , -1.4)),
            8: ('E11', (-1.0,  +0.0 , -1.4)),
            9: ('H2',  (-1.0,  -1.0 , -1.4)),
            10:('H5',  (-1.0,  -1.0 , -1.4)),
            11:('H8',  (-1.0,  -1.0 , -1.4)),
            12:('H11', (-1.0,  -1.0 , -1.4))
        }

        return heater_plate, hs_offsets


    def get_tip(self, pipette):
        """Pick up the next available tip for the given pipette, with rack limit check."""
        next_tip_index = self.tip_log[pipette]['next']
        tips = self.tip_log[pipette]['tips']
        
        if next_tip_index >= len(tips):
            raise RuntimeError(f"❌ No more tips available for {pipette.name}. Tip rack is empty!")

        tip = tips[next_tip_index]
        pipette.pick_up_tip(tip)
        self.tip_log[pipette]['next'] += 1

    def reset_tips(self, pipette=None):
        if pipette:
            pipette.reset_tipracks()
        else:
            self.pip300.reset_tipracks()
            self.pip20.reset_tipracks()


    def mara_distribute(self, df: pd.DataFrame, variable, source_id, tip_start = None):
        """
        Distribute volumes from a source to destination wells using either pip20 or pip300
        depending on volume per well.
        """
        if tip_start is None:
            tip_start = 'A1'
        else:
            tip_start = tip_start

        vols = df[variable].values.round(1)
        self.dests = df['well'].values

        if len(vols) != len(self.dests):
            raise ValueError("Volume list length must match number of destinations")

        pairs = list(zip(vols, self.dests))

        # Separate volumes by pipette type
        pip20_pairs = [(v, d) for v, d in pairs if 1 <= v <= self.pip20.max_volume]

        pip300_pairs = [(v, d) for v, d in pairs if v > self.pip20.max_volume]
        # print(pip20_pairs)
        # print(pip300_pairs)

        def distribute_with_pipette(pipette, pairs, tiprack):
            pipette.starting_tip = tiprack.wells_by_name()[tip_start]  # Set the starting tip for the pipette
            pipette.pick_up_tip()
            idx = 0
            while idx < len(pairs):
                max_vol = pipette.max_volume
                # Determine how many wells can be handled in one aspiration
                batch = []
                total = 0
                while idx < len(pairs):
                    v, _ = pairs[idx]
                    if total + v <= max_vol:
                        batch.append(pairs[idx])
                        total += v
                        idx += 1
                    else:
                        break

                # Aspirate once from source (assume fixed source, or add argument if needed)
                pipette.aspirate(total, self.plate_24[source_id].bottom(1))  # or another defined source
                pipette.move_to(self.plate_24[source_id].top(1))  # Move to the first destination well
                self.protocol.delay(seconds=2)  # Allow time for the aspirate to settle
                # Dispense into each destination
                for v, d in batch:
                    pipette.dispense(v, self.plate_96[d].top().move(Point(x=2.0, y=0.0, z=-5)))

                pipette.blow_out(self.trash_bin)
            pipette.drop_tip()

        # Perform distribution for each pipette type
        if pip20_pairs:
            distribute_with_pipette(self.pip20, pip20_pairs, self.tiprack_20)
        if pip300_pairs:
            distribute_with_pipette(self.pip300, pip300_pairs, self.tiprack_300)
        
        print(f"Started at {tip_start} and next tip is {self.tiprack_300.next_tip()}")
        print(f"Distribution complete for {variable} from source {source_id}.")
        
        #self.print_cmd()

    def final_mix(self, tip_start = None):
        if tip_start is not None:
            self.pip300.starting_tip = self.tiprack_300.wells_by_name()[tip_start]

        # Start mixing protocol
        print("Starting mixing protocol.")
        num_samples = len(df['well'].values)
        if num_samples > 96:
            raise ValueError("Cannot have more than 96 destination wells (96 rows).")
        
        well_names = df['well']
        dest_wells = [self.plate_96.wells_by_name()[name] for name in well_names]

        # Final Mix
        for well in dest_wells:
            #self.pick_up_tip(self.pip300)
            self.pip300.pick_up_tip()
            self.pip300.mix(25, 200, well.bottom(1), rate = 200)
            self.pip300.drop_tip()

        print("Final Mixing complete!")
        print(f"Next tip is {self.tiprack_300.next_tip()}")
        #self.print_cmd()
        #self.clear_commands()
    
    def distribute_all(self, df, columns, tip_start): 
        for source_id , col in zip(self.source_wells, columns):
            self.mara_distribute(df, col, source_id, tip_start)
            self.clear_commands()

    def mixing(self, df, columns, tip_start): 
        for source_id , col in zip(self.source_wells, columns):
            self.mara_distribute(df, col, source_id, tip_start)
            self.clear_commands()
            # print(self.pip300.next_tip()) # Prints out the next available tip (Including those that did not get iterated when reset)
        self.final_mix()

    def start_heater(self):
        '''
        heater_mod: heater module from labware
        heater_plate: heater plate from labware
        '''
        # Close the opentron flap and start heater
        self.hs_mod.close_labware_latch()
        self.hs_mod.set_and_wait_for_temperature(95)
        print("✅ Heater Started")
        # self.print_cmd()

    def stop_heater(self):
        '''
        Turns off the heater and opens the latch
        '''
        self.hs_mod.deactivate_heater()
        self.hs_mod.open_labware_latch()
        print("🛑 Heater Stopped")
        # self.print_cmd()

    def dropcasting(self, df: pd.DataFrame):
        '''
        Perform dropcasting from 96-well to 384-well with manual tip tracking.
        mix_well: array of stock locations
        hs_well: array of well locations
        volume: integer volume, Recommended 2 µL
        '''
        aspirate_volume = 5
        drop_volume = 1.5
        anneal_time = df['Anneal Time'].tolist()
        sample_wells = df['well'].tolist()
        

        if len(df) > len(self.hs_wells):
            raise ValueError(f":x: Too many samples ({len(df)}). Only {len(self.hs_wells)} destination wells are supported.")

        for i, (src, time) in enumerate(zip(sample_wells, anneal_time), start=1):
            if i not in self.hs_wells:
                raise ValueError(f"Missing HS well mapping for sample index {i}.")

            dest_well, offset = self.hs_wells[i]

            self.pip20.pick_up_tip()

            # Aspirate from 96-well plate
            self.pip20.aspirate(aspirate_volume, self.plate_96.wells_by_name()[src].bottom(1))

            # Dispense into 384-well with specified offset
            self.pip20.dispense(
                drop_volume,
                self.hs_plate.wells_by_name()[dest_well].bottom(0.05).move(Point(*offset))
            )

            self.protocol.delay(seconds=1)

            self.pip20.drop_tip()

            # Log or trigger anneal time
            
            add_material(f"Sample: {dest_well}", time)

    def dropcast_selected(self, source, destination, drop_volume=3):
        '''
        Perform dropcasting for selected wells from 96-well to 384-well.
        source: list of well names from the 96-well plate
        destination: list of integer keys for the heater shaker wells (1-12)
    
        volume: integer volume, Recommended 2 µL
        '''

        # Source wells (from mixture)
        selected_rows = df[df['well'].isin(source)].copy()
        selected_rows = pd.concat([selected_rows[selected_rows['well'] == s].iloc[[0]] for s in source], ignore_index=True)
        anneal_time = selected_rows['Anneal Time'].tolist()
        sample_wells = selected_rows['well'].tolist()
        # Destination plate (on heater)
        destinations = [self.hs_wells[d] for d in destination]
        # Volume to drop cast
        drop_volume = drop_volume
        aspirate_volume = drop_volume*2

        if len(selected_rows) > len(destinations):
            raise ValueError(f":x: Too many samples ({len(df)}). Only {len(destinations)} destination wells are supported.")
        
        # drop casting
        for src, dest_idx, time in zip(sample_wells, destination, anneal_time):
            well_name, offset = self.hs_wells[dest_idx]
            self.pip20.pick_up_tip()
            self.pip20.aspirate(aspirate_volume , self.plate_96.wells_by_name()[src].bottom(1))
            self.pip20.dispense(drop_volume, self.hs_plate.wells_by_name()[well_name].bottom(0.05).move(Point(*offset)))
            # self.pip20.blow_out(self.hs_plate.wells_by_name()[well_name].bottom(0.5).move(Point(*offset)))
            self.protocol.delay(seconds=1)
            self.pip20.drop_tip()
            add_material(f"Sample: {well_name}", time)

        # print(":white_check_mark: Complete Dropcasting")
        # self.print_cmd()

    def dropcast_manual(self, source, destination, drop_volume=3):
            '''
            Perform dropcasting from 96-well to 384-well with manual tip tracking.
            mix_well: array of stock locations
            hs_well: array of well locations
            volume: integer volume, Recommended 2 µL
            '''

            # Source wells (from mixture)
            sample_wells = source
            # Destination plate (on heater)
            destinations = destination # [self.hs_wells[d] for d in destination]
            # Volume to drop cast
            drop_volume = drop_volume
            aspirate_volume = drop_volume + 3

            # drop casting
            for src, dest_idx in zip(sample_wells, destinations):
                well_name, offset = self.hs_wells[dest_idx]
                self.pip20.pick_up_tip()
                self.pip20.aspirate(aspirate_volume, self.plate_96.wells_by_name()[src].bottom(1))
                self.pip20.dispense(drop_volume, self.hs_plate.wells_by_name()[well_name].bottom(0.01).move(Point(*offset)))
                #self.pip20.blow_out(self.hs_plate.wells_by_name()[well_name].bottom(0.5).move(Point(*offset)))
                self.protocol.delay(seconds=1)
                self.pip20.drop_tip()

    def position_testing(self, source, destination, drop_volume=3):
        '''
        Perform dropcasting from 96-well to 384-well with manual tip tracking.
        mix_well: array of stock locations
        hs_well: array of well locations
        volume: integer volume, Recommended 2 µL
        '''

        sample_wells = source

        # destination is a list of integer keys: [1, 2, 3, ...]
        destinations = [self.hs_wells[d] for d in destination]  # each is (well_name, offset)

        aspirate_volume = drop_volume

        self.pip20.pick_up_tip()
        for src, (well_name, offset) in zip(sample_wells, destinations):
            self.pip20.aspirate(aspirate_volume, self.plate_24.wells_by_name()[src].bottom(1))
            self.pip20.dispense(drop_volume, self.hs_plate.wells_by_name()[well_name].bottom(0.01).move(Point(*offset)))
            self.protocol.delay(seconds=1)
        self.pip20.drop_tip()


    def print_cmd(self):
        print("Printing Opentron Commands:")
        for cmd in self.protocol.commands():
            print(cmd)
    

    def clear_commands(self):
        self.protocol._commands.clear()

    def drop_all_tips(self):
        """Drop all tips from both pipettes."""
        self.pip300.drop_tip()
        self.pip20.drop_tip()

# Store all timers
active_timers = {}

class TimerThread(threading.Thread):
    def __init__(self, material_id, duration_min):
        super().__init__()
        self.material_id = material_id
        self.duration = timedelta(minutes=duration_min)
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.duration

    def run(self):
        time.sleep(self.duration.total_seconds())
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Material {self.material_id} is done!")

def add_material(material_id, duration_min):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Timer started for {material_id} ({duration_min} min)")
    thread = TimerThread(material_id, duration_min)
    active_timers[material_id] = thread
    thread.start()