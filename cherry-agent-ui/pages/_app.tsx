import type { AppProps } from 'next/app'
import { AgentProvider } from '../contexts/AgentContext'
import '../styles/globals.css'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AgentProvider>
      <Component {...pageProps} />
    </AgentProvider>
  )
}

export default MyApp
