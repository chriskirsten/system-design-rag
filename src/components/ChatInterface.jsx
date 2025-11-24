import { useState, useEffect } from "react"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Badge } from "./ui/badge"
import { Send, Sparkles } from "lucide-react"

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [renderKey, setRenderKey] = useState(0)

  const exampleQuestions = [
    "How does load balancing work?",
    "What is database sharding?",
    "Explain caching strategies",
    "What are microservices?",
  ]

  useEffect(() => {
    setRenderKey(prev => prev + 1)
  }, [messages])

  const handleSubmit = async (question) => {
    const userQuestion = question || input
    
    if (!userQuestion.trim()) {
      return
    }

    const userMessage = {
      id: `user-${Date.now()}-${Math.random()}`,
      type: "user",
      content: userQuestion,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/.netlify/functions/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userQuestion }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage = {
        id: `assistant-${Date.now()}-${Math.random()}`,
        type: "assistant",
        content: data.answer,
        sources: data.sources || [],
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      console.error('Query error:', err)
      setError('Failed to get answer. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const getSimilarityColor = (score) => {
    if (score > 0.8) return "bg-emerald-500"
    if (score > 0.6) return "bg-amber-500"
    return "bg-gray-400"
  }

  return (
    <div key={renderKey} className="flex flex-col h-screen bg-background relative overflow-hidden">
      {/* Background Gradient */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/95 to-primary/30" />
        <div className="absolute top-0 right-0 w-[1000px] h-[1000px] bg-gradient-to-bl from-primary/40 via-primary/20 to-transparent blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-gradient-to-tl from-primary/30 via-primary/10 to-transparent blur-3xl" />
      </div>

      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <header className="border-b border-border/40 bg-card/50 backdrop-blur-md sticky top-0 z-10">
  <div className="px-6 py-4">
    <div className="flex items-center gap-3">
      <div className="p-2 rounded-lg bg-primary shadow-[0_0_15px_rgba(20,184,166,0.3)]">
        <Sparkles className="h-7 w-7 text-primary-foreground" />
      </div>
      <div>
        <h1 className="text-2xl font-extrabold">Blueprint</h1>
        <p className="text-sm text-muted-foreground">Your AI guide to system design concepts</p>
      </div>
    </div>
  </div>
</header>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="container mx-auto px-4 py-6 max-w-4xl">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8">
                <div className="text-center space-y-2">
                  <div className="inline-flex p-4 rounded-full bg-primary mb-4">
                    <Sparkles className="h-12 w-12 text-primary-foreground" />
                  </div>
                  <h2 className="text-3xl font-bold">How can I help you today?</h2>
                  <div className="flex justify-center mt-3">
                    <div className="h-[3px] w-[60px] bg-primary rounded-full" />
                  </div>
                  <p className="text-muted-foreground text-lg pt-2">Choose an example or ask your own question</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                  {exampleQuestions.map((question, index) => (
                    <Card
                      key={index}
                      className="p-5 cursor-pointer border-2 border-l-[3px] border-l-primary transition-all duration-200 hover:bg-[#0d4f4a] hover:scale-105"
                      onClick={() => handleSubmit(question)}
                    >
                      <p className="text-sm font-medium">{question}</p>
                    </Card>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[85%] ${message.type === "user" ? "w-auto" : "w-full"}`}>
                      <Card className={`p-4 ${message.type === "user" ? "bg-primary text-primary-foreground border-0" : "bg-card"}`}>
                        {message.type === "user" ? (
                          <p>{message.content}</p>
                        ) : (
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              h2: (props) => <h2 className="text-xl font-bold text-foreground mt-6 mb-3 first:mt-0" {...props} />,
                              h3: (props) => <h3 className="text-lg font-semibold text-foreground mt-4 mb-2" {...props} />,
                              p: (props) => <p className="text-foreground leading-relaxed mb-3" {...props} />,
                              strong: (props) => <strong className="font-bold text-teal-400" {...props} />,
                              ul: (props) => <ul className="list-disc list-inside space-y-1 mb-3 text-foreground ml-4" {...props} />,
                              ol: (props) => <ol className="list-decimal list-inside space-y-1 mb-3 text-foreground ml-4" {...props} />,
                              li: (props) => <li className="text-foreground" {...props} />,
                              code: (props) => {
                                const {inline, children, ...rest} = props
                                return inline ? (
                                  <code className="bg-slate-800 text-teal-400 px-1.5 py-0.5 rounded text-sm font-mono" {...rest}>
                                    {children}
                                  </code>
                                ) : (
                                  <code className="block bg-slate-900 text-teal-400 p-4 rounded-lg overflow-x-auto my-3 text-sm font-mono" {...rest}>
                                    {children}
                                  </code>
                                )
                              },
                              pre: (props) => <pre className="bg-slate-900 rounded-lg p-0 overflow-x-auto my-3" {...props} />
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        )}
                      </Card>

                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 space-y-2">
                          <p className="text-xs font-semibold text-muted-foreground px-1">SOURCES</p>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                            {message.sources.map((source, index) => (
                              <Card 
                                key={index} 
                                className="p-3 hover:shadow-lg hover:border-primary hover:bg-primary/10 hover:scale-[1.02] transition-all duration-200"
                              >
                                <div className="space-y-2">
                                  <div className="flex items-start justify-between gap-2">
                                    <h4 className="text-sm font-medium leading-tight">
                                      {source.title}
                                    </h4>
                                    <Badge variant="secondary" className="shrink-0 text-xs">
                                      {source.category}
                                    </Badge>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                                      <div
                                        className={`h-full ${getSimilarityColor(source.similarity)} transition-all`}
                                        style={{ width: `${source.similarity * 100}%` }}
                                      />
                                    </div>
                                    <span className="text-xs font-semibold text-muted-foreground">
                                      {Math.round(source.similarity * 100)}%
                                    </span>
                                  </div>
                                </div>
                              </Card>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <Card className="p-4 bg-card">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                    </Card>
                  </div>
                )}

                {error && (
                  <div className="flex justify-center">
                    <Card className="p-4 bg-destructive/10 border-destructive">
                      <p className="text-sm text-destructive">{error}</p>
                    </Card>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-border/40 bg-card/50 backdrop-blur-md sticky bottom-0">
          <div className="container mx-auto px-4 py-4 max-w-4xl">
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit() }} className="flex gap-3">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit()
                    }
                  }}
                  placeholder="Ask a question about system design..."
                  className="w-full px-4 py-4 border border-[rgba(20,184,166,0.3)] rounded-lg resize-none focus:outline-none focus:ring-[2px] focus:ring-[#14b8a6] min-h-[80px] max-h-[200px] bg-card/80 text-foreground placeholder:text-muted-foreground/50"
                  rows={1}
                />
              </div>
              <Button
                type="submit"
                size="lg"
                disabled={!input.trim() || isLoading}
                className="bg-primary hover:bg-primary/90 text-primary-foreground w-[48px] h-[48px] p-0"
              >
                <Send className="h-5 w-5" />
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}