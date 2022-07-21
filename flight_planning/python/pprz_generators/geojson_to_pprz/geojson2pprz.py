import numpy as np
import json

# Imports for opening a file from a file dialog
import tkinter as tk
from tkinter import filedialog

class PprzFP(object):
    def __init__(self, ground_alt, alt, fp_name = 'MP2 flightplan', N = 50):
        # Configure pprz flightplan
        self.ground_alt = ground_alt
        self.alt = alt
        self.fp_name = fp_name
        self.N = N
        self.fp_xml = ''

        # Init Doctype
        self.fp_xml += '<!DOCTYPE flight_plan SYSTEM "../flight_plan.dtd">\n\n'

        # Ask to open a geojson file
        # If creating a PprzFP object, open a file dialog box to open a geojson file (.geojson)
        root = tk.Tk()
        root.withdraw()

        self.geojson_path = filedialog.askopenfilename(filetypes=[("geojson files", ".geojson")])

        f = open(self.geojson_path,"r")
        # Convert json to python dict
        self.geo_dict = json.load(f)['features']
        f.close()

        self.generate_fp()

    def generate_fp(self):
        self.home_lat_lon = self.generate_home_lat_lon() 
        #self.stdby_lat_lon = self.generate_stdby_lat_lon() # Will be start location
        #self.climb_lat_lon = self.generate_climb_lat_lon() # Will be start location
        #self.ldg_lat_lon = self.generate_ldg_lat_lon() # Will be start location
        self.buf_lat_lon = self.generate_buf_lat_lon()

        self.soft_gf_wp, self.soft_gf_sector = self.generate_soft_gf()
        self.hard_gf_wp, self.hard_gf_sector = self.generate_hard_gf()

        ########################
        # Construct flightplan #
        ########################

        # Add flight_plan section
        self.fp_xml += '<flight_plan alt="' + str(self.alt) + '" ground_alt="' + str(self.ground_alt) + '" lat0="' + str(self.home_lat_lon[0]) + '" lon0="' + str(self.home_lat_lon[1]) + '"  max_dist_from_home="500" name="' + str(self.fp_name) + '" security_height="10">\n'

        # Add header
        self.fp_xml += '\t<header>\n'

        self.fp_xml += '\t\t#include "autopilot.h"\n'
        self.fp_xml += '\t\t#include "modules/datalink/datalink.h"\n'
        self.fp_xml += '\t\t#include "modules/radio_control/radio_control.h"\n'
        self.fp_xml += '\t\t#include "modules/nav/waypoints.h"\n'
        self.fp_xml += '\t\t#include "modules/mp2/mp2_control.h"\n'

        # end header
        self.fp_xml += '\t</header>\n'

        # Add waypoints
        self.fp_xml += '\t<waypoints>\n'

        self.fp_xml += '\t\t<waypoint name="HOME" lat="' + str(self.home_lat_lon[0]) + '" lon="' + str(self.home_lat_lon[1]) + '"/>\n'
        self.fp_xml += '\t\t<waypoint name="CLIMB" lat="' + str(self.home_lat_lon[0]) + '" lon="' + str(self.home_lat_lon[1]) + '"/>\n'
        self.fp_xml += '\t\t<waypoint name="STDBY" lat="' + str(self.home_lat_lon[0]) + '" lon="' + str(self.home_lat_lon[1]) + '"/>\n'
        self.fp_xml += '\t\t<waypoint name="TD" lat="' + str(self.home_lat_lon[0]) + '" lon="' + str(self.home_lat_lon[1]) + '"/>\n'
        self.fp_xml += '\t\t<waypoint name="OWNPOS" lat="' + str(self.home_lat_lon[0]) + '" lon="' + str(self.home_lat_lon[1]) + '"/>\n'
        self.fp_xml += self.soft_gf_wp
        self.fp_xml += self.hard_gf_wp
        self.fp_xml += '\t\t<waypoint name="p1" lat="' + str(self.home_lat_lon[0]) + '" lon="' + str(self.home_lat_lon[1]) + '"/>\n'

        for i in range(self.N):
            self.fp_xml += '\t\t<waypoint name="p' + str(i+1) + 'a" lat="' + str(self.buf_lat_lon[0]) + '" lon="' + str(self.buf_lat_lon[1]) + '"/>\n'
        for i in range(self.N):
            self.fp_xml += '\t\t<waypoint name="p' + str(i+1) + 'b" lat="' + str(self.buf_lat_lon[0]) + '" lon="' + str(self.buf_lat_lon[1]) + '"/>\n'

        # end waypoints
        self.fp_xml += '\t</waypoints>\n'

        # Add sectors
        self.fp_xml += '\t<sectors>\n'
        
        self.fp_xml += self.soft_gf_sector
        self.fp_xml += self.hard_gf_sector

        # end sectors
        self.fp_xml += '\t</sectors>\n'

        # Add exceptions
        self.fp_xml += '\t<exceptions>\n'

        f = open('flight_planning/python/pprz_generators/geojson_to_pprz/templates/standard_exceptions.xml', 'r')
        std_exception_lines = f.readlines()
        f.close()

        for line in std_exception_lines:
            self.fp_xml += '\t\t' + line
        self.fp_xml += '\n'

        #self.fp_xml += '\t\t<exception cond="' + "Or(!InsideHardGeofence(GetPosX(), GetPosY()), GetPosAlt() @GT GetAltRef() + 80) @AND !(nav_block == IndexOfBlock('Wait GPS')) @AND !(nav_block == IndexOfBlock('Geo init')) @AND !(nav_block == IndexOfBlock('Holding point'))" + '" deroute="Holding point"/>'
        #self.fp_xml += '\t\t<exception cond="' + "Or(!InsideSoftGeofence(GetPosX(), GetPosY()), GetPosAlt() @GT GetAltRef() + 80) @AND !(nav_block == IndexOfBlock('Wait GPS')) @AND !(nav_block == IndexOfBlock('Geo init')) @AND !(nav_block == IndexOfBlock('Holding point'))" + '" deroute="Standby"/>'
        #self.fp_xml += '\t\t<exceprion cond='
        #self.fp_xml += '\t\t<exception cond="And(radio_control.status == RC_REALLY_LOST, datalink_time > 25) && !(nav_block == IndexOfBlock(' + "'Wait GPS'" + ')) && !(nav_block == IndexOfBlock(' + "'Geo init'" + ')) && !(nav_block == IndexOfBlock(' + "'Holding point'" + ')) && !(nav_block == IndexOfBlock(' + "'Pilot Permission Granted'" + ')) && !(nav_block == IndexOfBlock(' + "'Waiting For FP Upload'" + ')) && !(nav_block == IndexOfBlock(' + "'Wait For Execution Command'" + ')) && !(nav_block == IndexOfBlock(' + "'Counting Down For Start'" + ')) && !(nav_block == IndexOfBlock(' + "'land here'" + ')) && !(nav_block == IndexOfBlock(' + "'land'" + ')) && !(nav_block == IndexOfBlock(' + "'descend'" + ')) && !(nav_block == IndexOfBlock(' + "'flare'" + ')) && !(nav_block == IndexOfBlock(' + "'flare_low'" + ')) && !(nav_block == IndexOfBlock(' + "'landed'" + '))" deroute="land here"/>\n'
        #self.fp_xml += '\t\t<exception cond="datalink_time > 5 && !(nav_block == IndexOfBlock(' + "'Wait GPS'" + ')) && !(nav_block == IndexOfBlock(' + "'Geo init'" + ')) && !(nav_block == IndexOfBlock(' + "'Holding point'" + ')) && !(nav_block == IndexOfBlock(' + "'Pilot Permission Granted'" + ')) && !(nav_block == IndexOfBlock(' + "'Waiting For FP Upload'" + ')) && !(nav_block == IndexOfBlock(' + "'Wait For Execution Command'" + ')) && !(nav_block == IndexOfBlock(' + "'Counting Down For Start'" + ')) && !(nav_block == IndexOfBlock(' + "'Standby'" + ')) && !(nav_block == IndexOfBlock(' + "'land here'" + ')) && !(nav_block == IndexOfBlock(' + "'land'" + ')) && !(nav_block == IndexOfBlock(' + "'descend'" + ')) && !(nav_block == IndexOfBlock(' + "'flare'" + ')) && !(nav_block == IndexOfBlock(' + "'flare_low'" + ')) && !(nav_block == IndexOfBlock(' + "'landed'" + '))" deroute="land"/>\n'
        
        # End exceptions
        self.fp_xml += '\t</exceptions>\n'

        # Add blocks
        self.fp_xml += '\t<blocks>\n'

        f = open('flight_planning/python/pprz_generators/geojson_to_pprz/templates/standard_blocks.xml', 'r')
        std_block_lines = f.readlines()
        f.close()

        for line in std_block_lines:
            self.fp_xml += '\t\t' + line
        self.fp_xml += '\n'

        self.fp_xml += self.generate_mp2_blocks_xml()

        # End blocks
        self.fp_xml += '\t</blocks>\n'

        # end flight_plan section
        self.fp_xml += '</flight_plan>'

        print(self.fp_xml)

        fp_file = open(self.geojson_path[:-7] + 'xml', 'w')
        fp_file.write(self.fp_xml)
        fp_file.close()
        
        return

    def get_lat_lon(self, latlon_name):
        latlon_found = False
        i = 0
        point = {}
        while not latlon_found and i < len(self.geo_dict):
            # Check if geo_dict matches latlon 
            if self.geo_dict[i]['properties']['name'] == latlon_name:
                point = self.geo_dict[i]
                latlon_found = True
            i += 1

        coordinate = point['geometry']['coordinates']
        lon = coordinate[0]
        lat = coordinate[1]
        return (lat, lon)


    def generate_home_lat_lon(self):
        # Ask home point name
        home_name = input('Enter Home name: ')
        return self.get_lat_lon(home_name)
    '''
    def generate_stdby_lat_lon(self):
        # Ask stdby point name
        stdby_name = input('Enter Stdby name: ')
        return self.get_lat_lon(stdby_name)

    def generate_climb_lat_lon(self):
        # Ask climb point name
        climb_name = input('Enter climb name: ')
        return self.get_lat_lon(climb_name)

    def generate_ldg_lat_lon(self):
        # Ask ldg point name
        ldg_name = input('Enter ldg name: ')
        return self.get_lat_lon(ldg_name)
    '''
    def generate_buf_lat_lon(self):
        # Ask buf point name
        buf_name = input('Enter buf name: ')
        return self.get_lat_lon(buf_name)
    
    def get_latlon_list(self, coordinates_name):
        # Find coordinates with name
        coordinates_found = False
        i = 0
        geometry_dict = {}
        while not coordinates_found and i < len(self.geo_dict):
            # Check if geo_dict matches sector name
            if self.geo_dict[i]['properties']['name'] == coordinates_name:
                geometry_dict = self.geo_dict[i]
                coordinates_found = True
            i += 1
        
        # Generate a latlon list
        coordinates = geometry_dict['geometry']['coordinates'][0]
        latlon_list = []
        for i in range(len(coordinates) - 1):
            lon = coordinates[i][0]
            lat = coordinates[i][1]
            latlon = [lat, lon]
            latlon_list.append(latlon)

        return latlon_list
    
    def generate_soft_gf(self):
        # First ask sector name
        sector_name = input('Enter SGF sector name: ')

        # Generate latlon_list
        latlon_list = self.get_latlon_list(sector_name)
        
        # Convert coordinates to pprz waypoints
        waypoint_str = ''
        sector_str = '\t\t<sector color="yellow" name="SoftGeofence">\n'
        for i in range(len(latlon_list)):
            name = "SGF" + str(i+1)
            lat = latlon_list[i][0]
            lon = latlon_list[i][1]
            waypoint_str += '\t\t<waypoint name="' + name + '" lon="' + str(lon) + '" lat="' + str(lat) + '"/>\n'

            sector_str += '\t\t\t<corner name="' + str(name) + '"/>\n'
        
        sector_str += '\t\t</sector>\n'
        return waypoint_str, sector_str

    def generate_hard_gf(self):
        # First ask sector name
        sector_name = input('Enter HGF sector name: ')

        # Generate latlon_list
        latlon_list = self.get_latlon_list(sector_name)
        
        # Convert coordinates to pprz waypoints
        waypoint_str = ''
        sector_str = '\t\t<sector color="red" name="HardGeofence">\n'
        for i in range(len(latlon_list)):
            name = "HGF" + str(i+1)
            lat = latlon_list[i][0]
            lon = latlon_list[i][1]
            waypoint_str += '\t\t<waypoint name="' + name + '" lon="' + str(lon) + '" lat="' + str(lat) + '"/>\n'

            sector_str += '\t\t\t<corner name="' + str(name) + '"/>\n'
        
        sector_str += '\t\t</sector>\n'
        return waypoint_str, sector_str
    
    def generate_mp2_blocks_xml(self):
        blocks_xml = ''

        blocks_xml += '\t\t<block name="hold">\n'
        blocks_xml += '\t\t\t<call_once fun="waypoint_set_here(WP_OWNPOS)"/>\n'
        blocks_xml += '\t\t\t<stay wp="OWNPOS"/>\n'
        blocks_xml += '\t\t</block>\n'

        blocks_xml += '\t\t<block name="stay_p1">\n'
        blocks_xml += '\t\t\t<exception cond="And(mp2_get_fp_activated(), mp2_a_active())" deroute="line1a"/>'
        blocks_xml += '\t\t\t<exception cond="And(mp2_get_fp_activated(), !mp2_a_active())" deroute="line1b"/>'
        blocks_xml += '\t\t\t<stay wp="p1"/>\n'
        blocks_xml += '\t\t</block>\n'

        blocks_xml += '\t\t<block name="line1a">\n'
        blocks_xml += '\t\t\t<exception cond="mp2_finished_fp()" deroute="hold"/>\n'
        blocks_xml += '\t\t\t<call_once fun="waypoint_set_here(WP_OWNPOS)"/>\n'
        blocks_xml += '\t\t\t<call_once fun="mp2_set_airspeed()"/>\n'
        blocks_xml += '\t\t\t<call_once fun="mp2_update_active_wp_id()"/>\n'
        blocks_xml += '\t\t\t<go from="OWNPOS" hmode="route" wp="p1a"/>\n'
        blocks_xml += '\t\t</block>\n'

        for i in range(self.N-1):
            blocks_xml += '\t\t<block name="line' + str(i+2) + 'a">\n'
            blocks_xml += '\t\t\t<exception cond="mp2_finished_fp()" deroute="hold"/>\n'
            blocks_xml += '\t\t\t<call_once fun="mp2_set_airspeed()"/>\n'
            blocks_xml += '\t\t\t<call_once fun="mp2_update_active_wp_id()"/>\n'
            blocks_xml += '\t\t\t<go from="p' + str(i+1) + 'a" hmode="route" wp="p' + str(i+2) + 'a"/>\n'
            blocks_xml += '\t\t</block>\n'

        blocks_xml += '\t\t<block name="line1b">\n'
        blocks_xml += '\t\t\t<exception cond="mp2_finished_fp()" deroute="hold"/>\n'
        blocks_xml += '\t\t\t<call_once fun="waypoint_set_here(WP_OWNPOS)"/>\n'
        blocks_xml += '\t\t\t<call_once fun="mp2_set_airspeed()"/>\n'
        blocks_xml += '\t\t\t<call_once fun="mp2_update_active_wp_id()"/>\n'
        blocks_xml += '\t\t\t<go from="OWNPOS" hmode="route" wp="p1b"/>\n'
        blocks_xml += '\t\t</block>\n'

        for i in range(self.N-1):
            blocks_xml += '\t\t<block name="line' + str(i+2) + 'b">\n'
            blocks_xml += '\t\t\t<exception cond="mp2_finished_fp()" deroute="hold"/>\n'
            blocks_xml += '\t\t\t<call_once fun="mp2_set_airspeed()"/>\n'
            blocks_xml += '\t\t\t<call_once fun="mp2_update_active_wp_id()"/>\n'
            blocks_xml += '\t\t\t<go from="p' + str(i+1) + 'b" hmode="route" wp="p' + str(i+2) + 'b"/>\n'
            blocks_xml += '\t\t</block>\n'
            
        return blocks_xml
    
PprzFP(-2, 8)