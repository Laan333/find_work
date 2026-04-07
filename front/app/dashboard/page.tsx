"use client"

import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Header } from '@/components/dashboard/header'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { RecentVacancies } from '@/components/dashboard/recent-vacancies'
import { SearchQueriesCard } from '@/components/dashboard/search-queries-card'
import { AnalyticsCharts } from '@/components/dashboard/analytics-charts'
import { ApiError, fetchAnalytics, fetchSearches, fetchVacancies } from '@/lib/api'
import type { Analytics, SearchQuery, Vacancy } from '@/lib/types'

const emptyAnalytics: Analytics = {
  totalVacancies: 0,
  newToday: 0,
  analyzed: 0,
  applied: 0,
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

  useEffect(() => {
    const load = async () => {
      try {
        const [a, v, s] = await Promise.all([
          fetchAnalytics(),
          fetchVacancies({ pageSize: 8 }),
          fetchSearches(),
        ])
        setAnalytics(a)
        setVacancies(v.items)
        setQueries(s.slice(0, 5))
      } catch (e) {
        if (e instanceof ApiError) {
          toast.error(`Дашборд: ошибка ${e.status}`)
        }
      }
    }
    void load()
  }, [])

  return (
    <div className="flex flex-col h-full">
      <Header title="Дашборд" subtitle="Обзор вакансий и аналитика" />

      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <StatsCards analytics={analytics} />

        <AnalyticsCharts analytics={analytics} />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <RecentVacancies vacancies={vacancies} />
          </div>
          <div>
            <SearchQueriesCard queries={queries} />
          </div>
        </div>
      </div>
    </div>
  )
}
