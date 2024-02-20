import { useState, useEffect } from 'react';

import { Header } from "./components/header"
import { Footer } from "./components/footer"
import { VideoBox } from "./components/videobox"
import { VideoIcon } from "./components/icons"
import { ObjectFilterInput } from "./components/objectFilter"

import { VideoId, VideoInfo, VideoInfoResponse, VideoData, VideoObjectRanking, ObjectFilter } from "./models"

export const API_BASE_URL = process.env.REACT_APP_VIDEO_STREAMS_API_URL

function VideoSection() {

  const [loading, setLoading] = useState<boolean>(true)
  const [videoIds, setVideoIds] = useState<VideoId[]>([])
  const [videoInfos, setVideoInfos] = useState<VideoInfo[]>([])
  const [videoObjectRankings, setVideoObjectRankings] = useState<VideoObjectRanking[]>([])
  const [objectFilters, setObjectFilters] =  useState<ObjectFilter[] | null>(null)
  // const [selectedIds, setSelectedIds] =   useState<VideoId[]>(videoIds)

  useEffect(() => {
    setLoading(true)
    async function fetchVideoIds() {
      const response = await fetch(
        `${API_BASE_URL}/video_stream`
        )
      const resp: {video_streams: VideoId[]} = await response.json();
      setVideoIds(resp.video_streams)
    }
    fetchVideoIds()
    }, 
    []
  )

  useEffect(() => {
    async function fetchVideoInfos() {
      const videoIdsString: string = videoIds.map((videoId) => videoId.video_id).join(",")
      const response = await fetch(
        `${API_BASE_URL}/video_stream_info?ids=${videoIdsString}`
        )
      const resp: VideoInfoResponse = await response.json();
      setVideoInfos(resp.video_infos)
    }
    fetchVideoInfos()
    }, 
    [videoIds]
  )

  useEffect(() => {
    async function fetchVideoObjectRanking() {
      const videoIdsString: string = videoIds.map((videoId) => videoId.video_id).join(",")
      const response = await fetch(
        `${API_BASE_URL}/video_stream/object_rankings?ids=${videoIdsString}`
        )
      const resp: VideoObjectRanking[] = await response.json();
      setVideoObjectRankings(resp)
      setLoading(false)
    }

    fetchVideoObjectRanking()
    
    }, 
    [videoIds]
  )

  var selectedIds: VideoId[]  = videoIds
  if (objectFilters !== null) {
    selectedIds = []
    videoObjectRankings.map((videoObjectRanking) => {
      objectFilters.map((objectFilter) => {
        if (videoObjectRanking.object_names.includes(objectFilter)) {
          selectedIds.push({
            source_name: videoObjectRanking.source_name,
            video_id: videoObjectRanking.video_id
          })
        }
      })
    })
    selectedIds = Array.from(new Set(selectedIds))
  }

  const videoDatas: VideoData[] = selectedIds.map((videoId) => {
    const videoInfo = videoInfos.filter((videoInfo) => videoInfo.video_id === videoId.video_id)[0]
    const videoObjectRanking = videoObjectRankings.filter((videoObjectRanking) => videoObjectRanking.video_id === videoId.video_id)[0]
    return {
      videoId: videoId,
      videoInfo: videoInfo,
      videoObjectRanking: videoObjectRanking
    }
  })

  

  // console.log(videoDatas)

  return (
    <section className="w-full py-12 bg-gray-100 dark:bg-gray-800">
    <div className="container px-4 md:px-6">
      <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Livestreams</h2>
      <div className="flex justify-between items-center mt-4">
        <div className="flex-initial w-full max-w-md mx-4">
          <div className=" z-40">
            <ObjectFilterInput
              onClick={setObjectFilters}
            />
          </div>
        </div>
        
        {/* <div className="flex-initial w-full max-w-md mx-4">
          <Input placeholder="Filter by tags..." type="search" />
        </div>
        <div className="flex-initial w-full max-w-md mx-4">
          <Slider className="w-full h-10 pl-3 pr-6 text-base placeholder-gray-600 border rounded-lg appearance-none focus:shadow-outline">
          </Slider>
        </div> */}
      </div>

      {
        loading ?
        <div className="grid mt-16 gap-4 justify-items-center" style={{filter: "blur(2px)"}} >
          <h3 className="text-3xl text-bold animate-pulse" >Loading...</h3>
          <VideoIcon className="blur-sm animate-spin h-36 w-36" />
        </div>
        :
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-8">
        {
          videoDatas.map((videoData) => 
            <VideoBox 
              key={videoData.videoId.video_id + videoData.videoId.source_name} 
              videoId={videoData.videoId}
              videoInfo={videoData.videoInfo}
              videoObjectRanking={videoData.videoObjectRanking}
              // onClick={setObjectFilters}
              // objectFilters={objectFilters}
            ></VideoBox>
          )
        }
      </div>
      }
      
      
      {/*  */}
    </div>
  </section>
  )
}


export default function App() {
  return (
    <div key="1" className="flex flex-col min-h-screen">
      <Header></Header>
      <main className="flex-1">
        <VideoSection></VideoSection>
      </main>
      <Footer></Footer>
    </div>
  )
}



// function IntroSection() {
//   return <section className="w-full py-12">
//     <div className="container px-4 md:px-6">
//       <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
//         <img
//           alt="Hero"
//           className="mx-auto aspect-video overflow-hidden rounded-xl object-cover object-center sm:w-full lg:order-last"
//           height="310"
//           src="/placeholder.svg"
//           width="550"
//         />
//         <div className="flex flex-col justify-center space-y-4">
//           <div className="space-y-2">
//             <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
//               Welcome to LiveStream ML
//             </h1>
//             <p className="max-w-[600px] text-gray-500 md:text-xl dark:text-gray-400">
//               Discover and select livestreams for ML object detection.
//             </p>
//           </div>
//           <div className="w-full max-w-md">
//             <Input placeholder="Search for a livestream..." type="search" />
//           </div>
//         </div>
//       </div>
//     </div>
//   </section>
// }