**Used Throughout**

tidyverse [https://www.tidyverse.org/packages/](https://www.tidyverse.org/packages/)  

* lubridate cheat sheet: [https://lubridate.tidyverse.org/](https://lubridate.tidyverse.org/) 

**Sourcing Data**

**Basic information, *catapultR* package**  
Install catapultR package: [https://catapultr.catapultsports.com/installation\_demo.html](https://catapultr.catapultsports.com/installation_demo.html)  
Primary documentation: [https://catapultr.catapultsports.com/](https://catapultr.catapultsports.com/)  
Cheat sheet/function overview: [https://catapultr.catapultsports.com/cheat\_sheets.html](https://catapultr.catapultsports.com/cheat_sheets.html)  
   
**Accessing 10Hz data from *catapultR***  
General process: [https://catapultr.catapultsports.com/get\_tenHz\_demo.html](https://catapultr.catapultsports.com/get_tenHz_demo.html)  
ofCloudGetActivities(token)  
ofCloudGetAthleteDevicesInActivity(token, activity\_id)  
ofCloudGetActivitySesnsorData(token, activity\_id, athlete\_id)  
   
**Basic Information, *cfbfastR* package (college users only)**  
Install cfbfastR & get API key: [https://cfbfastr.sportsdataverse.org/articles/intro.html](https://cfbfastr.sportsdataverse.org/articles/intro.html)  
Play-by-Play Data: [https://cfbfastr.sportsdataverse.org/reference/cfbd\_pbp\_data.html](https://cfbfastr.sportsdataverse.org/reference/cfbd_pbp_data.html)  
cfbd\_pbp\_data(year, season\_type, week, team)

**Combining 10Hz & Play-by-Play Data**

Animations with gganimate (examples: [https://gganimate.com/](https://gganimate.com/))  
Plain tables with flextable: [https://ardata-fr.github.io/flextable-book/](https://ardata-fr.github.io/flextable-book/)   
Workload table with reactable: [https://glin.github.io/reactable/articles/examples.html](https://glin.github.io/reactable/articles/examples.html) 

* Extensions with reactablfmtr: [https://kcuilla.github.io/reactablefmtr/](https://kcuilla.github.io/reactablefmtr/) 

**Velocity Profiling**

Find peaks with pracma::findpeaks: [https://cran.r-project.org/web/packages/pracma/index.html](https://cran.r-project.org/web/packages/pracma/index.html)   
NLS models stats::nls: [https://www.rdocumentation.org/packages/stats/versions/3.6.2/topics/nls](https://www.rdocumentation.org/packages/stats/versions/3.6.2/topics/nls) 

* Extensions for bootstrapping, etc: [https://cran.r-project.org/web/packages/nlstools/index.html](https://cran.r-project.org/web/packages/nlstools/index.html)    
* nlstools::nlsBoot; nlstools::nlsBootPredict

**Additional References**

**Clavel, P., Leduc, C., Morin, J. B., Owen, C., Samozino, P., Peeters, A., ... & Lacome, M. (2022)**. Concurrent validity and reliability of sprinting force–velocity profile assessed with GPS devices in elite athletes. *International journal of sports physiology and performance*, *17*(10), 1527-1531.

**Samozino, P., Rabita, G., Dorel, S., Slawinski, J., Peyrot, N., Saez de Villarreal, E., & Morin, J. B. (2016)**. A simple method for measuring power, force, velocity properties, and mechanical effectiveness in sprint running. *Scandinavian journal of medicine & science in sports*, *26*(6), 648-658.

**Wellman, A. D., Coad, S. C., Goulet, G. C., & McLellan, C. P. (2016)**. Quantification of competitive game demands of NCAA division I college football players using global positioning systems. *The Journal of Strength & Conditioning Research*, *30*(1), 11-19.