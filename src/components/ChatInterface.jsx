import { useState } from "react"
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Badge } from "./ui/badge"
import { ScrollArea } from "./ui/scroll-area"
import { Send, Sparkles } from "lucide-react"

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const exampleQuestions = [
    "How does load balancing work?",
    "What is database sharding?",
    "Explain caching strategies",
    "What are microservices?",
  ]

  const handleSubmit = async (question) => {
    const userQuestion = question || input
    if (!userQuestion.trim()) return

    const userMessage = {
      id: Date.now().toString(),
      type: "user",
      content: userQuestion,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setError(null)

    try {
      // Call YOUR Netlify Function
      const response = await fetch('http://localhost:8888/.netlify/functions/query', {
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
        id: (Date.now() + 1).toString(),
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
    <div className="flex flex-col h-screen bg-background relative overflow-hidden animate-in fade-in duration-500">
      {/* Background Gradient */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/95 to-primary/30" />
        <div className="absolute top-0 right-0 w-[1000px] h-[1000px] bg-gradient-to-bl from-primary/40 via-primary/20 to-transparent blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-gradient-to-tl from-primary/30 via-primary/10 to-transparent blur-3xl" />
      </div>

      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <header className="border-b border-border/40 bg-card/50 backdrop-blur-md sticky top-0 z-10">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary shadow-[0_0_15px_rgba(20,184,166,0.3)]">
                <Sparkles className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-balance">Blueprint</h1>
                <p className="text-sm text-muted-foreground">Your AI guide to system design concepts</p>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <ScrollArea className="flex-1">
          <div className="container mx-auto px-4 py-6 max-w-4xl">
            {messages.length === 0 ? (
              // Empty State
              <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8">
                <div className="text-center space-y-2">
                  <div className="inline-flex p-4 rounded-full bg-primary mb-4 shadow-[0_0_40px_rgba(20,184,166,0.3)]">
                    <Sparkles className="h-12 w-12 text-primary-foreground" />
                  </div>
                  <h2 className="text-3xl font-bold text-balance">How can I help you today?</h2>
                  <div className="flex justify-center mt-3">
                    <div className="h-[3px] w-[60px] bg-primary rounded-full" />
                  </div>
                  <p className="text-muted-foreground text-lg pt-2">Choose an example or ask your own question</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                  {exampleQuestions.map((question, index) => (
                    <Card
                      key={index}
                      className="p-5 cursor-pointer border-2 border-l-[3px] border-l-primary transition-all duration-200 ease-in-out hover:bg-[#0d4f4a] hover:border-l-primary hover:shadow-[0_0_15px_rgba(20,184,166,0.5)] hover:scale-105 animate-in slide-in-from-bottom-4 fade-in"
                      style={{ animationDelay: `${index * 100}ms`, animationDuration: "500ms" }}
                      onClick={() => handleSubmit(question)}
                    >
                      <p className="text-sm font-medium text-balance">{question}</p>
                    </Card>
                  ))}
                </div>
              </div>
            ) : (
              // Chat Messages
              <div className="space-y-6">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[85%] ${message.type === "user" ? "w-auto" : "w-full"}`}>
                      <Card
                        className={`p-4 ${message.type === "user" ? "bg-primary text-primary-foreground border-0" : "bg-card"}`}
                      >
                        {message.type === "user" ? (
                          <p className="text-pretty">{message.content}</p>
                        ) : (
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <p className="whitespace-pre-wrap">{message.content}</p>
                          </div>
                        )}
                      </Card>

                      {/* Source Cards */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 space-y-2">
                          <p className="text-xs font-semibold text-muted-foreground px-1">SOURCES</p>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                            {message.sources.map((source, index) => (
                              <Card key={index} className="p-3 hover:shadow-md hover:border-primary/30 transition-all">
                                <div className="space-y-2">
                                  <div className="flex items-start justify-between gap-2">
                                    <h4 className="text-sm font-medium leading-tight text-balance">{source.title}</h4>
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

                {/* Loading Animation */}
                {isLoading && (
                  <div className="flex justify-start">
                    <Card className="p-4 bg-card">
                      <div className="flex gap-1">
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        />
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        />
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        />
                      </div>
                    </Card>
                  </div>
                )}

                {/* Error Message */}
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
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t border-border/40 bg-card/50 backdrop-blur-md sticky bottom-0">
          <div className="container mx-auto px-4 py-4 max-w-4xl">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleSubmit()
              }}
              className="flex gap-3"
            >
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
                  className="w-full px-4 py-4 border border-[rgba(20,184,166,0.3)] rounded-lg resize-none focus:outline-none focus:ring-[2px] focus:ring-[#14b8a6] focus:shadow-[0_0_30px_rgba(20,184,166,0.4)] focus:border-transparent min-h-[80px] max-h-[200px] bg-card/80 text-foreground placeholder:text-muted-foreground/50 placeholder:text-[15px] shadow-[0_0_20px_rgba(20,184,166,0.15)] transition-all duration-200"
                  rows={1}
                />
              </div>
              <Button
                type="submit"
                size="lg"
                disabled={!input.trim() || isLoading}
                className="bg-primary hover:bg-primary/90 hover:shadow-[0_0_25px_rgba(20,184,166,0.6)] text-primary-foreground w-[48px] h-[48px] p-0 transition-all duration-200"
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