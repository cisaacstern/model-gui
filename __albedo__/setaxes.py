import albedo._albedo.setrasters as setrasters
#import _albedo.setrasters as setrasters
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits import axisartist    

class SetAxes(setrasters.SetRasters):    
    def set_axes(self, figsize=(23.75,10), topMargin=0.9, 
                    bottomMargin=0.1, leftMargin=0.05, rightMargin=0.9):
            '''
            instantiates the axes for the timeSeries_Plot.
            broken into a separate function to reduce the line count for timeSeries_Plot
            '''
            fig = plt.figure(figsize=figsize, dpi=self.dpi)
            ax = host_subplot(111, axes_class=axisartist.Axes)
            
            par1 = ax.twinx()
            par2 = ax.twinx()
            par2.axis["right"] = par2.new_fixed_axis(loc="right", offset=(50, 0))
            par3 = ax.twinx()
            par3.axis["right"] = par3.new_fixed_axis(loc="right", offset=(100, 0))
            
            par1.axis["right"].toggle(all=True)
            par2.axis["right"].toggle(all=True)
            par3.axis["right"].toggle(all=True)
            
            ax.set_ylabel(r"$Radiation  (watts/m^2)$")
            par1.set_ylabel("M")
            par2.set_ylabel("Albedo")
            par3.set_ylabel(r"$Visible Surface (m^2)$")
            
            ax.set_ylim(0, 1200) #radiation y-range
            par1.set_ylim(0, 3) #terrain correction y-range
            par2.set_ylim(0.2, 0.8) #albedo y-range
            par3.set_ylim(0.0, 3.0) #vis% y-range
                    
            ax.axis["left"].label.set_color('darkorange') #label color, radiation y-axis
            par1.axis["right"].label.set_color('darkmagenta') #label color, M y-axis
            par2.axis["right"].label.set_color('darkturquoise') #label color, Albedo y-axis
            par3.axis["right"].label.set_color('k') #label color, viz y-axis

            ax.margins(0, tight=True)
            plt.subplots_adjust(top=topMargin, bottom=bottomMargin,
                                left=leftMargin, right=rightMargin)
            ax.grid()
            par1.grid(alpha=0.5)
            
            self.fig, self.ax = fig, ax
            self.par1, self.par2, self.par3 = par1, par2, par3
            return