"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import type { SearchQuery } from '@/lib/types'
import { Search, Clock, MapPin, Plus, Play, Pause } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface SearchQueriesCardProps {
  queries: SearchQuery[]
  onToggleActive?: (query: SearchQuery) => void
}

export function SearchQueriesCard({ queries, onToggleActive }: SearchQueriesCardProps) {
  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes} мин`
    return `${Math.floor(minutes / 60)} ч`
  }

  return (
    <Card className="border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold">Поисковые запросы</CardTitle>
        <Button variant="outline" size="sm" asChild>
          <Link href="/dashboard/search">
            <Plus className="w-4 h-4 mr-1" />
            Добавить
          </Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        {queries.map((query) => (
          <div 
            key={query.id} 
            className={cn(
              "p-4 rounded-lg border border-border/50 transition-colors",
              query.isActive ? "bg-card" : "bg-muted/30"
            )}
          >
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Search className="w-4 h-4 text-primary" />
                  <span className="font-medium text-foreground truncate">{query.keyword}</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  {query.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {query.location}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    каждые {formatTime(query.interval)}
                  </span>
                </div>
              </div>
              <Switch
                checked={query.isActive}
                onCheckedChange={() => onToggleActive?.(query)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs">
                  {query.vacanciesFound} вакансий
                </Badge>
                <Badge variant="outline" className="text-xs">
                  hh.ru
                </Badge>
              </div>
              <Badge 
                className={cn(
                  "text-xs",
                  query.isActive ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
                )}
              >
                {query.isActive ? (
                  <><Play className="w-3 h-3 mr-1" /> Активен</>
                ) : (
                  <><Pause className="w-3 h-3 mr-1" /> Пауза</>
                )}
              </Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
