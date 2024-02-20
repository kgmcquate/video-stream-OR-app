
export function PlusIcon(props: { className: string }) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12h14" />
      <path d="M12 5v14" />
    </svg>
  )
}
  
  
export function VideoIcon(props: { className: string }) {
  return (
    <svg 
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="100" 
      height="100"
      viewBox="0 0 100 100"
    >
    <circle cx="50" cy="50" r="20" fill="#353535" stroke="#919191" strokeWidth="10" />

    <circle 
        cx="50" cy="50" r="40" fill="transparent"
        stroke="#525252" stroke-width="7"  
        strokeDashoffset="0" strokeDasharray="210" 
    />
    <circle fill="#525252" cx="90" cy="50" r="3.5" />
    <circle fill="#525252" cx="70.1" cy="15.38" r="3.5" />

    <g transform="rotate(180)" transform-origin="center"> 
        <circle 
            cx="50" cy="50" r="30" fill="transparent"
            stroke="#464646" stroke-width="4"  
            strokeDashoffset="0" strokeDasharray="160" 
        />
        <circle fill="#464646" cx="80" cy="50" r="2" />
        <circle fill="#464646" cx="67.8" cy="25.85" r="2" />
    </g>
  </svg>
  )
}
  
export function ChevronRightIcon(props: { className: string }) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m9 18 6-6-6-6" />
    </svg>
  )
}


export function PlayIcon(props: { className: string }) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  )
}
  