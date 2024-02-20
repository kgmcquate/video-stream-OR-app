import { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import * as Plotly from "plotly.js";

import { Button } from "./button"
import { PopoverTrigger, PopoverContent, Popover } from "./popover"
import { ChevronRightIcon, PlayIcon, PlusIcon } from "./icons"

import { VideoObjectCounts, VideoId } from "../models"

import { API_BASE_URL } from "../App"
// /video_stream/objects_stats

export function VideoStatsBox({ videoId, className }: { videoId: VideoId, className: string }) {
    const [objectCounts, setObjectCounts] = useState<VideoObjectCounts[]>([])

    useEffect(() => {
        async function fetchVideoStats() {
            const response = await fetch(
                `${API_BASE_URL}/video_stream/object_counts?ids=${videoId.video_id}`
            )
            const resp: VideoObjectCounts[] = await response.json();

            setObjectCounts(resp)
        }

        fetchVideoStats()
    }, [videoId])

    function darkenColor(color: string, percent: number = 100) {
        const num = parseInt(color.slice(1), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return "#" + (0x1000000 + (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 + (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 + (B < 255 ? (B < 1 ? 0 : B) : 255)).toString(16).slice(1);
    }

    const dotColors = ["#FB8500",  "#219EBC", "#023047", "#FFB703", "#2a9d8f", "#780000"  ]
    const lineColors = ["#975000",  "#145f71", "#011d2b", "#9b6f00","#195e56", "#480000" ] // dotColors.map((color) => "#000000")
    // console.log(lineColors)

    var index = -1

    console.log(objectCounts.length)

    const mapData: Plotly.Data[] = objectCounts.map((videoObjectCounts) => {
        index += 1
        return {
            name: videoObjectCounts.object_name,
            // orientation: 'h',
            x: videoObjectCounts.video_times,
            y: videoObjectCounts.avg_num_objects,
            textposition: "middle right",
            hovertemplate: "%{y:.2f}",
            xhoverformat: "%b %-d, %-H:%M" ,
            // yhoverformat: "",
            textfont: {
                family: 'system-ui'
            },
            type: 'bar',
            // type: 'scatter',
            // mode: 'lines+markers',
            marker: { 
                color: dotColors[index], 
                // symbol: "circle-open-dot",
                // size: 8
            },
            // line: {
            //     color: lineColors[index],
            //     shape: "spline",
            //     smoothing: 0.85,
            //     width: 2
            // }
        }
    })

    // console.log(mapData)

    return (
        <div className={className}>
            <Popover>
                <PopoverTrigger asChild>
                    <Button
                        className="flex gap-2 items-center w-full"
                        style={{
                            maxWidth: "100px"
                        }}
                        // variant="outline"
                        size="sm"
                    >
                        <span>Analytics</span>
                        <ChevronRightIcon className="w-4 h-4" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-4">
                    <div className="">
                        <Plot
                            data={mapData}
                            layout={
                                {
                                    width: 360,
                                    height: 300,
                                    barmode: 'stack',
                                    title: {
                                        text: 'Object Counts',
                                        font: {
                                            family: 'system-ui',
                                            size: 20
                                        },
                                        xanchor: "center",
                                        yanchor: "top"
                                    },
                                    showlegend: true,
                                    legend: {"orientation": "h"},
                                    margin: {
                                        t: 16,
                                        b: 16,
                                        l: 20,
                                        r: 16,
                                        pad: 0
                                    }
                                }
                            }
                            config={{displayModeBar: false}}
                        />
                    </div>
                </PopoverContent>
            </Popover>
        </div>
    )
}