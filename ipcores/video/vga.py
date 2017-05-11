# vga_sync.py
# ===========
# 
# VGA sync generator 
# 
# Author : 
#     Hugo Arboleas, <harboleas@citedef.gob.ar>
# 
##############################################################################
# 
# Copyright 2015 Hugo Arboleas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from myhdl import *

def vga_sync(clk50_i,
             rst_i,
             hs_o,
             vs_o,
             act_vid_o,
             x_o,
             y_o) :
 
    """
    VGA sync generator (800x600 @ 72Hz) 

    Inputs

    * clk50_i - Pixel clock 50Mhz
    * rst_i   - Reset 

    Outputs

    * hs_o      - Horizontal sync
    * vs_o      - Vertical sync
    * act_vid_o - Active video 
    * x_o       - Coordenada X del pixel actual [0 - 799]
    * y_o       - Coordenada Y del pixel actual [0 - 599]

    """
 
    ######################################
    # Horizontal (en pixels)
    H_SYNC = 120
    H_FRONT = 56
    H_ACT = 800
    H_BACK = 64
    H_TOTAL = H_SYNC + H_FRONT + H_ACT + H_BACK
    ######################################    
    # Vertical (en lineas)
    V_SYNC = 6
    V_FRONT = 37
    V_ACT = 600
    V_BACK = 23
    V_TOTAL = V_SYNC + V_FRONT + V_ACT + V_BACK
    ####################     

    h_cont = Signal(intbv(0, 0, H_TOTAL))     # contadores 
    v_cont = Signal(intbv(0, 0, V_TOTAL))
    act_vid = Signal(False)
    x = Signal(intbv(0, 0, H_ACT))
    y = Signal(intbv(0, 0, V_ACT))


    @always(clk50_i.posedge, rst_i.posedge)
    def contadores() :
        if rst_i :  
            h_cont.next = 0
            v_cont.next = 0

        else :
            if h_cont == H_TOTAL - 1 :
                h_cont.next = 0

                if v_cont == V_TOTAL - 1 :
                    v_cont.next = 0
                else :
                    v_cont.next = v_cont + 1

            else :
                h_cont.next = h_cont + 1
    
    @always_comb
    def comp() :
        # Horiz. sync
        if h_cont < H_SYNC :
            hs_o.next = True
        else :
            hs_o.next = False
        # Vert. sync
        if v_cont < V_SYNC :
            vs_o.next = True
        else :
            vs_o.next = False


        if h_cont < H_SYNC + H_FRONT :
            x_o.next = 0
        elif h_cont >= H_SYNC + H_FRONT + H_ACT :
            x_o.next = 799
        else :
            x_o.next = h_cont - (H_SYNC + H_FRONT)

        if v_cont < V_SYNC + V_FRONT :
            y_o.next = 0
        elif v_cont >= V_SYNC + V_FRONT + V_ACT :
            y_o.next = 599
        else :
            y_o.next = v_cont - (V_SYNC + V_FRONT)

        if V_SYNC + V_FRONT - 1 < v_cont and v_cont < V_SYNC + V_FRONT + V_ACT and H_SYNC + H_FRONT - 1 < h_cont and h_cont < H_SYNC + H_FRONT + H_ACT :
            act_vid_o.next = True
        else :
            act_vid_o.next = False

    return instances()

#  vim: set ts=8 sw=4 tw=0 et :
