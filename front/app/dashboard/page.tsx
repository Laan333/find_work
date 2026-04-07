"use client"

import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Header } from '@/components/dashboard/header'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { RecentVacancies } from '@/components/dashboard/recent-vacancies'
import { SearchQueriesCard } from '@/components/dashboard/search-queries-card'
import { AnalyticsCharts } from '@/components/dashboard/analytics-charts'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ApiError, fetchAnalytics, fetchSearches, fetchVacancies } from '@/lib/api'
import type { Analytics, SearchQuery, Vacancy } from '@/lib/types'

const emptyAnalytics: Analytics = {
  totalVacancies: 0,
  newToday: 0,
  analyzed: 0,
  applied: 0,
  favorites: 0,
  avgSalary: 0,
  topSkills: [],
  vacanciesByDate: [],
  vacanciesBySource: [],
  vacanciesByExperience: [],
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Analytics>(emptyAnalytics)
  const [vacancies, setVacancies] = useState<Vacancy[]>([])
  const [queries, setQueries] = useState<SearchQuery[]>([])
  const [selectedSearchId, setSelectedSearchId] = useState<string>('all')

  useEffect(() => {
    const load = async () => {
      try {
        const [a, s] = await Promise.all([
          fetchAnalytics(),
          fetchSearches(),
        ])
        const selectedKeyword =
          selectedSearchId === 'all' ? undefined : s.find((q) => q.id === selectedSearchId)?.keyword
        const v = await fetchVacancies({ pageSize: 8, q: selectedKeyword })
        setAnalytics(a)
        setVacancies(v.items)
        setQueries(s)
      } catch (e) {
        if (e instanceof ApiError) {
          toast.error(`Дашборд: ошибка ${e.status}`)
        }
      }
    }
    void load()
  }, [selectedSearchId])

  return (
    <div className="flex flex-col h-full">
      <Header title="Дашборд" subtitle="Обзор вакансий и аналитика" />

      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <StatsCards analytics={analytics} />

        <AnalyticsCharts analytics={analytics} />

        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">Фильтр вакансий:</span>
          <Select value={selectedSearchId} onValueChange={setSelectedSearchId}>
            <SelectTrigger className="w-[320px]">
              <SelectValue placeholder="Все поисковые запросы" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все поисковые запросы</SelectItem>
              {queries.map((q) => (
                <SelectItem key={q.id} value={q.id}>
                  {q.keyword}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <RecentVacancies vacancies={vacancies} />
          </div>
          <div>
            <SearchQueriesCard queries={queries.slice(0, 5)} />
          </div>
        </div>
      </div>
    </div>
  )
}
