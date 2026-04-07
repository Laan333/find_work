"use client"

import { Card, CardContent } from '@/components/ui/card'
import { Briefcase, TrendingUp, Brain, Send, Banknote, Star } from 'lucide-react'
import type { Analytics } from '@/lib/types'
import { cn } from '@/lib/utils'

interface StatsCardsProps {
  analytics: Analytics
}

export function StatsCards({ analytics }: StatsCardsProps) {
  const stats = [
    {
      title: 'Всего вакансий',
      value: analytics.totalVacancies,
      change: '+12%',
      changeType: 'positive' as const,
      icon: Briefcase,
      color: 'text-primary'
    },
    {
      title: 'Новых сегодня',
      value: analytics.newToday,
      change: '+23',
      changeType: 'positive' as const,
      icon: TrendingUp,
      color: 'text-chart-1'
    },
    {
      title: 'Проанализировано',
      value: analytics.analyzed,
      change: '68%',
      changeType: 'neutral' as const,
      icon: Brain,
      color: 'text-chart-2'
    },
    {
      title: 'Откликов',
      value: analytics.applied,
      change: '+3',
      changeType: 'positive' as const,
      icon: Send,
      color: 'text-chart-3'
    },
    {
      title: 'Средняя зарплата',
      value: `${(analytics.avgSalary / 1000).toFixed(0)}K`,
      change: '+5%',
      changeType: 'positive' as const,
      icon: Banknote,
      color: 'text-chart-4'
    },
    {
      title: 'В избранном',
      value: 12,
      icon: Star,
      color: 'text-chart-5'
    }
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {stats.map((stat, index) => (
        <Card key={index} className="border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className={cn("w-10 h-10 rounded-lg bg-muted flex items-center justify-center", stat.color)}>
                <stat.icon className="w-5 h-5" />
              </div>
              {stat.change && (
                <span className={cn(
                  "text-xs font-medium px-2 py-0.5 rounded-full",
                  stat.changeType === 'positive' && "bg-primary/10 text-primary",
                  stat.changeType === 'neutral' && "bg-muted text-muted-foreground"
                )}>
                  {stat.change}
                </span>
              )}
            </div>
            <div className="text-2xl font-bold text-foreground">{stat.value}</div>
            <div className="text-xs text-muted-foreground mt-1">{stat.title}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
