"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { VacancyCard } from './vacancy-card'
import type { Vacancy } from '@/lib/types'
import { ArrowRight } from 'lucide-react'
import Link from 'next/link'

interface RecentVacanciesProps {
  vacancies: Vacancy[]
}

export function RecentVacancies({ vacancies }: RecentVacanciesProps) {
  return (
    <Card className="border-border/50">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold">Последние вакансии</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/dashboard/vacancies" className="flex items-center gap-1">
            Все вакансии
            <ArrowRight className="w-4 h-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {vacancies.slice(0, 3).map((vacancy) => (
          <VacancyCard key={vacancy.id} vacancy={vacancy} />
        ))}
      </CardContent>
    </Card>
  )
}
