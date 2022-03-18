/*Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. */


function createTimeLine(html_element, labels, data, type, suggested_min, suggested_max, labelString){
    
    var data = {
    labels: labels,
    datasets: [{
        label: type,
        data: data,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
    };

    var option = {
                    scales: {
                        y: {
                            suggestedMin: suggested_min,
                            suggestedMax: suggested_max,
                            title:{
                                display: true,
                                text: labelString
                            }, 
                            
                            ticks: {
                                    stepSize: 5
                                }
                            
                        },
                        x: {
                            title:{
                                display: true,
                                text: 'Last 24 hours'
                            }
                            
                        }
                    }
                };


    new Chart(html_element, {
        type: 'line',
        data: data,
        options: option           
        });
        
    }