import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Wand2, Sparkles, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function TypingText({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    let index = 0;
    setDisplayed("");
    if (!text) return;

    const interval = setInterval(() => {
      if (index >= text.length) {
        clearInterval(interval);
        return;
      }
      const char = text.charAt(index);
      setDisplayed((d) => d + char);
      index++;
    }, 20);

    return () => clearInterval(interval);
  }, [text]);

  return <p className="whitespace-pre-wrap text-gray-800 leading-relaxed text-lg font-sans">{displayed}</p>;
}

export default function AIInterface() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch("http://localhost:8001/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setAnswer(String(data.answer || "沒有回覆內容。"));
    } catch (error) {
      console.error(error);
      setAnswer("❌ 發生錯誤，請稍後再試。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-indigo-200 via-white to-pink-300 flex flex-col items-center justify-start px-6 py-16">
      <motion.h1
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="select-none text-5xl font-extrabold text-gray-900 mb-14 flex items-center gap-4 drop-shadow-lg"
      >
        <Sparkles className="text-indigo-600 h-12 w-12 animate-bounce" />
        AI MCP Agent
      </motion.h1>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-4xl bg-white/95 backdrop-blur-lg p-10 rounded-3xl shadow-2xl border border-gray-300 mb-10"
      >
        <Textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="請輸入問題或會議逐字稿..."
          className="w-full h-48 p-5 mb-8 rounded-xl border border-indigo-300 shadow-inner text-lg font-sans leading-relaxed resize-none focus:ring-4 focus:ring-indigo-400 transition"
        />
        <motion.div whileTap={{ scale: 0.95 }} whileHover={{ scale: 1.07 }} className="text-center">
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="font-semibold text-lg px-8 py-4 bg-indigo-600 hover:bg-indigo-700 shadow-lg rounded-xl"
          >
            {loading ? (
              <>
                <Loader2 className="mr-3 h-6 w-6 animate-spin" />
                正在分析...
              </>
            ) : (
              <>
                <Wand2 className="mr-3 h-6 w-6" />
                生成回覆
              </>
            )}
          </Button>
        </motion.div>
      </motion.div>

      <AnimatePresence>
        {answer && (
          <motion.div
            initial={{ opacity: 0, y: 70 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 30 }}
            transition={{ duration: 0.7 }}
            className="w-full max-w-4xl"
          >
            <Card className="bg-white shadow-2xl rounded-3xl border border-gray-200">
              <CardContent className="p-8 whitespace-pre-wrap text-gray-900 leading-loose text-lg font-serif">
                <TypingText text={answer} />
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
