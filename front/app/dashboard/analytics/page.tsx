"use client"

import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Header } from '@/components/dashboard/header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ApiError, fetchAnalytics, fetchSettings, fetchVacancies } from '@/lib/api'
import type { Analytics, Vacancy } from '@/lib/types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  AreaChart,
  Area,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts'
import { Briefcase, TrendingUp, Brain, Target, Banknote, Star } from 'lucide-react'

const COLORS = ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))', 'hsl(var(--chart-5))']

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

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<Analytics>(emptyAnalytics)
  const [vacancies, setVacancies] = useState<Vacancy[]>([])
  const [highMatchThreshold, setHighMatchThreshold] = useState(70)

  useEffect(() => {
    const load = async () => {
      try {
        const [a, v] = await Promise.all([fetchAnalytics(), fetchVacancies({ pageSize: 200 })])
        setAnalytics(a)
        setVacancies(v.items)
      } catch (e) {
        if (e instanceof ApiError) toast.error(`Аналитика: ${e.status}`)
      }
      try {
        const s = await fetchSettings()
        const t = Number(s.highMatchThreshold)
        if (!Number.isNaN(t)) setHighMatchThreshold(t)
      } catch {
        /* порог по умолчанию 70 */
      }
    }
    void load()
  }, [])

  const topSlice = analytics.topSkills.slice(0, 6)
  const maxSkillCount = Math.max(0, ...topSlice.map((s) => s.count))
  const radarFullMark = maxSkillCount < 1 ? 1 : Math.ceil(maxSkillCount * 1.1) || maxSkillCount

  const skillsRadarData = topSlice.map((s) => ({
    skill: s.skill,
    value: s.count,
    fullMark: radarFullMark,
  }))

  // Данные по зарплатам
  const salaryData = vacancies
    .filter(v => v.salary?.from)
    .map(v => ({
      title: v.title.length > 20 ? v.title.slice(0, 20) + '...' : v.title,
      from: v.salary?.from || 0,
      to: v.salary?.to || v.salary?.from || 0
    }))
    .slice(0, 6)

  // Статусы вакансий
  const statusData = [
    { name: 'Новые', value: vacancies.filter(v => v.status === 'new').length },
    { name: 'Просмотрены', value: vacancies.filter(v => v.status === 'viewed').length },
    { name: 'Отклики', value: vacancies.filter(v => v.status === 'applied').length },
    { name: 'Интервью', value: vacancies.filter(v => v.status === 'interview').length },
    { name: 'Отказы', value: vacancies.filter(v => v.status === 'rejected').length },
  ].filter(s => s.value > 0)

  const stats = [
    {
      title: 'Всего вакансий',
      value: analytics.totalVacancies,
      icon: Briefcase,
      color: 'text-primary'
    },
    {
      title: 'Новых сегодня',
      value: analytics.newToday,
      icon: TrendingUp,
      color: 'text-chart-1'
    },
    {
      title: 'Проанализировано',
      value: analytics.analyzed,
      icon: Brain,
      color: 'text-chart-2'
    },
    {
      title: `Совпадений ≥${highMatchThreshold}%`,
      value: vacancies.filter((v) => (v.matchScore || 0) >= highMatchThreshold).length,
      icon: Target,
      color: 'text-chart-3',
    },
    {
      title: 'Средняя зарплата',
      value: analytics.avgSalary > 0 ? `${(analytics.avgSalary / 1000).toFixed(0)}K` : '—',
      icon: Banknote,
      color: 'text-chart-4',
    },
    {
      title: 'В избранном',
      value: analytics.favorites ?? 0,
      icon: Star,
      color: 'text-chart-5',
    },
  ]

  return (
    <div className="flex flex-col h-full">
      <Header 
        title="Аналитика" 
        subtitle="Статистика и insights по вакансиям"
      />
      
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {stats.map((stat, index) => (
            <Card key={index} className="border-border/50">
              <CardContent className="p-4">
                <div className={`w-10 h-10 rounded-lg bg-muted flex items-center justify-center mb-3 ${stat.color}`}>
                  <stat.icon className="w-5 h-5" />
                </div>
                <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                <div className="text-xs text-muted-foreground mt-1">{stat.title}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Вакансии по дням */}
          <Card className="border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Динамика вакансий</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.vacanciesByDate}>
                    <defs>
                      <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                      tickFormatter={(value) => new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}
                    />
                    <YAxis tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="count"
                      stroke="hsl(var(--chart-1))"
                      fillOpacity={1}
                      fill="url(#colorCount)"
                      strokeWidth={2}
                      name="Вакансий"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Зарплаты */}
          <Card className="border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Диапазоны зарплат</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={salaryData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                    <XAxis 
                      type="number" 
                      tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                      tickFormatter={(value) => `${value / 1000}K`}
                    />
                    <YAxis 
                      type="category" 
                      dataKey="title" 
                      width={100}
                      tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => `${value.toLocaleString('ru-RU')} ₽`}
                    />
                    <Bar dataKey="from" fill="hsl(var(--chart-2))" name="От" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="to" fill="hsl(var(--chart-1))" name="До" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Топ навыки */}
          <Card className="border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Востребованные навыки</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={skillsRadarData}>
                    <PolarGrid stroke="hsl(var(--border))" />
                    <PolarAngleAxis 
                      dataKey="skill" 
                      tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <PolarRadiusAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                    <Radar
                      name="Количество"
                      dataKey="value"
                      stroke="hsl(var(--chart-1))"
                      fill="hsl(var(--chart-1))"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Источник */}
          <Card className="border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Источник вакансий</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] flex flex-col items-center justify-center">
                <div className="w-32 h-32 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary">{analytics.totalVacancies}</div>
                    <div className="text-xs text-muted-foreground mt-1">вакансий</div>
                  </div>
                </div>
                <div className="flex flex-col gap-2 w-full max-w-xs">
                  {analytics.vacanciesBySource.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center">Нет данных по источникам</p>
                  ) : (
                    analytics.vacanciesBySource.map((src, i) => (
                      <div
                        key={src.source}
                        className="flex items-center gap-3 px-4 py-2 bg-muted rounded-lg"
                      >
                        <div
                          className="w-3 h-3 rounded-full shrink-0"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        />
                        <span className="font-medium truncate">{src.source}</span>
                        <Badge variant="secondary" className="ml-auto shrink-0">
                          {src.count}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Статусы */}
          <Card className="border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Статусы вакансий</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                      nameKey="name"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {statusData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* По опыту */}
        <Card className="border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Вакансии по требуемому опыту</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.vacanciesByExperience}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis 
                    dataKey="experience" 
                    tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <YAxis tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))', 
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar 
                    dataKey="count" 
                    fill="hsl(var(--chart-2))" 
                    radius={[4, 4, 0, 0]}
                    name="Вакансий"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Топ навыки таблица */}
        <Card className="border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Рейтинг навыков</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {analytics.topSkills.map((skill, index) => (
                <div 
                  key={skill.skill}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl font-bold text-muted-foreground">
                      #{index + 1}
                    </span>
                    <span className="font-medium">{skill.skill}</span>
                  </div>
                  <Badge variant="secondary">{skill.count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
