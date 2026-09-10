# Alex Carnall — Jets (Catapult Workshop)

**Date:** January 29, 2025, 2:15 PM CST
**Transcript:** [Fireflies](https://app.fireflies.ai/view/Alex-Carnall-Jets::LLpvY7a2AOCT2wQw) (ID `LLpvY7a2AOCT2wQw`)
**Duration:** 63 min
**Participants:** eric.rash11@gmail.com

## Overview

The technical presentation and workshop led by Alex Carnall focused on analyzing 10 Hz data sourced from Catapult sensors, emphasizing its integration with play-by-play data. The session began with an introduction to the data structure and function demonstrations using the Catapult API, followed by a detailed exploration of combining 10 Hz data with the cfbfastR package, addressing challenges related to timestamp alignment. Participants learned about velocity profiles, their significance in performance assessment, and were shown mathematical modeling techniques to interpret these profiles effectively. The workshop also covered model fitting, validation, and the need for responsible interpretation of results, noting limitations and potential errors in the data. Attendees engaged in a Q&A session, raising inquiries on tactical influences and model enhancements, with action items suggested for further exploration of the catapultR package and position-specific modeling to refine analysis.

## Notes

### Introduction and Data Sourcing
- Alex Carnall introduces himself and the topic of the presentation
- Focus on 10 Hz data from Catapult sensors
- Demonstration of basic R functions to access data from Catapult API
- Explanation of 10 Hz data structure and content

### Combining 10 Hz Data with Play-by-Play
- Introduction to cfbfastR package for play-by-play data
- Challenges in aligning timestamps between 10 Hz and play-by-play data
- Process of creating a comprehensive data source combining 10 Hz and play-by-play data
- Demonstration of visualizing player movements during specific plays

### Velocity Profiles and Data Analysis
- Explanation of velocity profiles and their importance in performance analysis
- Setting criteria for qualifying runs (e.g., starting below 0.5 mph, continuous acceleration for 10+ yards)
- Introduction to modeling velocity profiles using mathematical functions
- Demonstration of how to interpret velocity profile graphs

### Model Fitting and Interpretation
- Detailed explanation of the mathematical model used for velocity profiles
- Discussion on the meaning of model parameters (VHmax and K)
- Visualization of model fitting process using bootstrap method
- Importance of differentiating between observed and predicted data in velocity curves

### Limitations and Responsible Interpretation
- Emphasis on cautious interpretation of model results
- Discussion on the limitations of the model and potential sources of error
- Importance of considering context (e.g., play type, field position) when interpreting results
- Demonstration of how to compare individual athletes to their position group

### Model Validation and Future Directions
- Comparison of model predictions to observed maximum velocities
- Discussion on the accuracy of the model at different distance ranges
- Suggestions for improving the model and data collection process
- Q&A on tactical influences, deceleration patterns, and potential model improvements

## Action Items (from the workshop)

- Explore the catapultR package for efficient data handling and analysis
- Consider implementing methods to separate on-field players from sideline players in data analysis
- Investigate the possibility of including deceleration patterns in the velocity profile model
- Explore position-specific modeling for more accurate velocity profiles
