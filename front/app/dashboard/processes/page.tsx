"use client"

import { useEffect, useMemo, useState } from 'react'
import { Header } from '@/components/dashboard/header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { fetchProcessLogs, fetchProcessStatus, type ProcessLogEventDto, type ProcessStatusDto } from '@/lib/api'

export default function ProcessesPage() {
  const [status, setStatus] = useState<ProcessStatusDto>({ active: false })
  const [logs, setLogs] = useState<ProcessLogEventDto[]>([])
  const [filter, setFilter] = useState<'all' | 'sync' | 'ai_match'>('all')
  const [quickFilter, setQuickFilter] = useState<'all' | 'waiting' | 'errors'>('all')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [s, l] = await Promise.all([fetchProcessStatus(), fetchProcessLogs(150)])
      setStatus(s)
      setLogs(l)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const [s, l] = await Promise.all([fetchProcessStatus(), fetchProcessLogs(150)])
        if (cancelled) return
        setStatus(s)
        setLogs(l)
      } catch {
        /* ignore */
      }
    }
    void poll()
    const id = setInterval(poll, status.active ? 2000 : 5000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [status.active])

  const filtered = useMemo(() => {
    const byType = filter === 'all' ? logs : logs.filter((x) => x.processType === filter)
    if (quickFilter === 'all') return byType
    if (quickFilter === 'waiting') {
      return byType.filter((x) => x.phase === 'waiting' || x.phase === 'rate_limited')
    }
    return byType.filter((x) => x.status === 'failed' || x.phase === 'error')
  }, [filter, logs, quickFilter])

  const statusBadgeVariant = (event: ProcessLogEventDto): 'default' | 'secondary' | 'destructive' | 'outline' => {
    if (event.status === 'failed' || event.phase === 'error') return 'destructive'
    if (event.phase === 'waiting' || event.phase === 'rate_limited') return 'outline'
    if (event.status === 'completed') return 'secondary'
    return 'default'
  }

  return (
    <div className="flex flex-col h-full">
      <Header title="Процессы и логи" subtitle="Статусы парсинга и AI-анализа в реальном времени" />
      <div className="flex-1 p-6 space-y-4 overflow-auto">
        <Card className="border-border/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Текущий статус</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {status.active ? (
              <>
                <div className="flex items-center gap-2">
                  <Badge>{status.processType === 'sync' ? 'Парсинг' : 'AI-анализ'}</Badge>
                  <Badge variant="outline">{status.phase || 'running'}</Badge>
                  {typeof status.progress === 'number' && <Badge variant="secondary">{status.progress}%</Badge>}
                </div>
                <p className="text-muted-foreground">{status.message || 'Выполняется процесс...'}</p>
              </>
            ) : (
              <div className="space-y-1">
                <p className="text-muted-foreground">Активных процессов нет.</p>
                <p className="text-xs text-muted-foreground">
                  Авто-анализ: {status.autoAnalyzeEnabled ? 'включен' : 'выключен'}
                  {status.autoAnalyzeEnabled && status.waiting && typeof status.waitSeconds === 'number'
                    ? `, ожидание ~${Math.max(1, Math.floor(status.waitSeconds / 60))} мин`
                    : ''}
                </p>
                {status.message && <p className="text-xs text-muted-foreground">{status.message}</p>}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex items-center gap-2">
          <Button variant={filter === 'all' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('all')}>
            Все
          </Button>
          <Button variant={filter === 'sync' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('sync')}>
            Парсинг
          </Button>
          <Button
            variant={filter === 'ai_match' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('ai_match')}
          >
            AI-анализ
          </Button>
          <Button variant="outline" size="sm" className="ml-auto" onClick={() => void load()} disabled={loading}>
            Обновить
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant={quickFilter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setQuickFilter('all')}
          >
            Все события
          </Button>
          <Button
            variant={quickFilter === 'waiting' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setQuickFilter('waiting')}
          >
            Ожидание
          </Button>
          <Button
            variant={quickFilter === 'errors' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setQuickFilter('errors')}
          >
            Ошибки
          </Button>
        </div>

        <div className="space-y-2">
          {filtered.map((e) => (
            <Card key={e.id} className="border-border/50">
              <CardContent className="p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="outline">{e.processType === 'sync' ? 'Парсинг' : 'AI-анализ'}</Badge>
                  <Badge variant={statusBadgeVariant(e)}>
                    {e.status}
                  </Badge>
                  <Badge variant={e.phase === 'waiting' || e.phase === 'rate_limited' ? 'outline' : 'secondary'}>
                    {e.phase}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(e.ts).toLocaleString('ru-RU')}
                  </span>
                </div>
                <div className="text-sm">{e.message}</div>
                {typeof e.progress === 'number' && (
                  <div className="text-xs text-muted-foreground mt-1">Прогресс: {e.progress}%</div>
                )}
                {e.counters && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {Object.entries(e.counters)
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(' · ')}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
          {!loading && filtered.length === 0 && (
            <div className="text-sm text-muted-foreground">Пока нет событий для выбранного фильтра.</div>
          )}
        </div>
      </div>
    </div>
  )
}
