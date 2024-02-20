import { useState, useEffect } from 'react';

import { Combobox } from '@headlessui/react'

import { Button } from "./button"
import { API_BASE_URL } from '../App';

import { ObjectRanking, ObjectFilter } from "../models"

const MAX_DISPLAYED_OPTIONS = 5

type searchItem = {
    id: string
    label: string
}

export function ObjectFilterInput({onClick}: {onClick: (objectFilter: ObjectFilter[] | null) => void}) {

    const [searchItems, setSearchItems] = useState<searchItem[]>([])

    const [selected, setSelected] = useState<string | null>('')
    const [query, setQuery] = useState('')

    const searchWords = query.toLowerCase().split(' ').map((s) => s.trim())
    const filteredItems =
        (query === ''
        ? searchItems
        : searchItems.filter((item) =>
            searchWords
                .map((searchWord) => item.label.toLowerCase().includes(searchWord))
                .reduce((a, b) => a || b)
            ||
            item.label
                .toLowerCase()
                .includes(query.toLowerCase()) //.replace(/\s+/g, '')
            )
        ).slice(0, MAX_DISPLAYED_OPTIONS)
        
    var selectedArray: string[] | null = null
    if (selected?.trim() === "") {
        selectedArray = null
    }  else {
        selectedArray = selected?.split(" ") ? selected?.split(" ").map((s) => s.trim()) : []
    }
        
    useEffect(() => {
        async function fetchVideoObjectRankings() {
            //video_stream_info?ids=Cp4RRAEgpeU
            const response = await fetch(
                `${API_BASE_URL}/video_stream/overall_object_rankings`
            )
    
            const rankingResponse: ObjectRanking[] = await response.json();

            const searchItemsResponse: searchItem[] = rankingResponse.map((ranking) => {
                return {
                    id: `${ranking.rank}`,
                    label: ranking.object_name
                }
            })

            // console.log(rankingResponse)
            setSearchItems(searchItemsResponse)
        }

        fetchVideoObjectRankings()
    }, []) //filteredItems

    return (
    <div className="flex">
    <Combobox value={selected}>
        <Combobox.Input 
            onChange={(event) => {
                    // const currentWord = event.target.value.split(" ").at(-1)
                    setQuery(event.target.value)
                    setSelected(event.target.value)
                }
            }
            onKeyDown={(event) => event.key === "Enter" ? onClick(selectedArray): null}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring  disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Search for objects..."
        />
        <Combobox.Options className="flex flex-col grow absolute mt-10 z-50 border-2 border-lightgray rounded-md bg-background">
          {filteredItems.map((item) => (
            <Combobox.Option 
                key={item.id} value={item.label}
                className="h-10 hover:bg-gray-300 p-2 border-lightgray "
                // onClick={(event) => setQuery(event.target)} 
                onClick={(event) => setSelected((event.target as HTMLElement).innerText)}
            >
              {item.label}
            </Combobox.Option>
          ))}
        </Combobox.Options>
      </Combobox>
      <Button onClick={(event) => {onClick(selectedArray)}}>Search</Button>
      </div>
    )
}


