# test.py
# =======
# 
# Test bench para el divisor secuencial de numeros sin signo 
# 
# Author: 
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

import unittest 
from myhdl import *
from udiv import udiv

class Test_udiv(unittest.TestCase) :

    def setUp(self) :

        self.clk = Signal(False)
        self.rst = Signal(False)
    
        self.start = Signal(False)
        self.done = Signal(False)
        self.div0 = Signal(False)

        self.a = Signal(intbv(10)[5:])
        self.b = Signal(intbv(0)[4:])
        self.q = Signal(intbv(0)[5:])
        self.r = Signal(intbv(0)[5:])

        self.dut = udiv(clk_i = self.clk,
                        rst_i = self.rst,
                        start_i = self.start,
                        a_i = self.a,
                        b_i = self.b,
                        done_o = self.done,
                        div0_o = self.div0,
                        q_o= self.q,
                        r_o = self.r)

        self.T_CLK = 20
        @always(delay(self.T_CLK / 2))
        def clk_gen():
            self.clk.next = not self.clk
        
        self.clk_gen = clk_gen

    #####################################################
    # Especificaciones del core en funcion de los test

    def test_div0(self) :
        """Test de error en la division por 0"""
        
        @instance
        def stimulus() :
            # Reset
            yield delay(15)
            self.rst.next = True
            yield delay(15)
            self.rst.next = False

            # Carga el dividendo y divisor 
            yield self.clk.negedge
            self.start.next = True
            self.a.next = 10
            self.b.next = 0
            # Verifica la duracion y el valor de las senales de done y div0 
            yield self.clk.posedge
            self.start.next = False
            yield delay(1)
            self.assertEqual(self.div0, True)
            self.assertEqual(self.done, True) 
            yield self.clk.posedge
            yield delay(1)
            self.assertEqual(self.div0, False)
            self.assertEqual(self.done, False) 


            # Verifica el efecto del reset en div0 
            yield self.clk.negedge
            self.start.next = True
            self.a.next = 10
            self.b.next = 0

            yield self.clk.posedge
            self.start.next = False
            yield delay(1)
            self.assertEqual(self.div0, True)
            self.assertEqual(self.done, True) 

            yield delay(10)    
            self.assertEqual(self.div0, True)  
            self.rst.next = True
            yield delay(1)
            self.assertEqual(self.div0, False) 
            self.assertEqual(self.done, False) 
            raise StopSimulation

        Simulation(self.dut, self.clk_gen, stimulus).run()

    def test_division(self) :
        """Test de division"""

        @instance
        def stimulus() :
            # Reset
            yield delay(15)
            self.rst.next = True
            yield delay(15)
            self.rst.next = False
            
            # Carga el dividendo y el divisor
            yield self.clk.negedge
            self.a.next = 24
            self.b.next = 5
            self.start.next = True
            yield self.clk.posedge
            t_ini = now()
            self.start.next = False
            # Espera que finalice la operacion
            yield self.done.posedge
            delta_t = now() - t_ini
            clocks = delta_t / self.T_CLK
            # Verifica el resultado
            self.assertEqual(self.q, self.a // self.b)
            self.assertEqual(self.r, self.a % self.b)
            # Verifica que la operacion se realice en n + 1 clks
            n = len(self.q)
            self.assertEqual(clocks, n + 1)
            
            yield delay(40)

            raise StopSimulation

        Simulation(self.dut, self.clk_gen, stimulus).run()

if __name__ == "__main__" :
    unittest.main()

# vim: set ts=8 sw=4 tw=0 et :
