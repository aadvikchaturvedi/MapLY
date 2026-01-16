import React, { ReactNode } from 'react'
import "@/styles/global.css"
const layout = ({children} : {children:ReactNode}) => {
  return (
    <div>{children}</div>
  )
}

export default layout