"use client"

import { useState, useEffect, useRef, useCallback } from 'react'
import { toast } from 'sonner'
import { Header } from '@/components/dashboard/header'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { SafeMarkdown } from '@/components/safe-markdown'
import { ApiError, fetchResume, postResumeUpload, putResume } from '@/lib/api'
import type { Resume } from '@/lib/types'
import { 
  FileText, 
  Upload, 
  Save, 
  User, 
  Mail, 
  Phone, 
  MessageCircle,
  Briefcase,
  GraduationCap,
  Code,
  Trash2,
  Plus,
  CheckCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'

const UPLOAD_ACCEPT = '.pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain'

const ALLOWED_EXT = new Set(['.pdf', '.docx', '.txt'])

const emptyResume: Resume = {
  id: '',
  title: '',
  fullName: '',
  position: '',
  experience: '',
  skills: [],
  education: '',
  about: '',
  contacts: {},
  rawText: '',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  isActive: true,
}

function resumeAsMarkdown(r: Resume): string {
  const blocks: string[] = [
    [`# ${r.position}`, r.fullName ? `**${r.fullName}**` : ''].filter(Boolean).join('\n'),
  ]
  if (r.rawText?.trim()) {
    blocks.push(r.rawText.trim())
  }
  blocks.push(
    `## Опыт\n\n${r.experience || '_не заполнено_'}`,
    `## Навыки\n\n${(r.skills || []).length ? r.skills.join(', ') : '_не заполнено_'}`,
    `## Образование\n\n${r.education || '_не заполнено_'}`,
    `## О себе\n\n${r.about || '_не заполнено_'}`,
  )
  return blocks.join('\n\n')
}

export default function ResumePage() {
  const [resume, setResume] = useState<Resume>(emptyResume)
  const [newSkill, setNewSkill] = useState('')
  const [isSaved, setIsSaved] = useState(false)
  const [fullResumeOpen, setFullResumeOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('edit')
  const [uploadBusy, setUploadBusy] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    void (async () => {
      try {
        const r = await fetchResume()
        if (r) setResume(r)
      } catch {
        /* 404 — оставляем пустое */
      }
    })()
  }, [])

  const handleSave = async () => {
    try {
      const saved = await putResume({
        title: resume.title,
        fullName: resume.fullName,
        position: resume.position,
        experience: resume.experience,
        skills: resume.skills,
        education: resume.education,
        about: resume.about,
        contacts: resume.contacts,
        rawText: resume.rawText,
        isActive: resume.isActive,
      })
      setResume(saved)
      setIsSaved(true)
      toast.success('Резюме сохранено')
      setTimeout(() => setIsSaved(false), 2000)
    } catch {
      toast.error('Не удалось сохранить')
    }
  }

  const handleAddSkill = () => {
    if (newSkill.trim() && !resume.skills.includes(newSkill.trim())) {
      setResume(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }))
      setNewSkill('')
    }
  }

  const handleRemoveSkill = (skill: string) => {
    setResume(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }))
  }

  const ingestUploadedFile = useCallback(async (file: File) => {
    const dot = file.name.lastIndexOf('.')
    const ext = dot >= 0 ? file.name.slice(dot).toLowerCase() : ''
    if (!ALLOWED_EXT.has(ext)) {
      toast.error('Нужен файл PDF, DOCX или TXT')
      return
    }
    setUploadBusy(true)
    try {
      const res = await postResumeUpload(file)
      setResume((prev) => ({ ...prev, rawText: res.rawText }))
      for (const w of res.warnings) {
        toast.warning(w)
      }
      if (res.warnings.length === 0) {
        toast.success(`Текст из «${res.fileName}» подставлен — проверьте черновик и нажмите «Сохранить»`)
      } else {
        toast.message('Проверьте черновик и нажмите «Сохранить»')
      }
      setActiveTab('edit')
    } catch (e) {
      if (e instanceof ApiError) {
        const detail =
          e.body && typeof e.body === 'object' && e.body !== null && 'detail' in e.body
            ? String((e.body as { detail?: unknown }).detail)
            : e.message
        toast.error(detail || `Ошибка ${e.status}`)
      } else {
        toast.error('Не удалось загрузить файл')
      }
    } finally {
      setUploadBusy(false)
    }
  }, [])

  return (
    <div className="flex flex-col h-full">
      <Header 
        title="Моё резюме" 
        subtitle="Управление резюме для анализа вакансий"
      />
      
      <div className="flex-1 p-6 overflow-auto">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="edit">Редактирование</TabsTrigger>
              <TabsTrigger value="preview">Предпросмотр</TabsTrigger>
              <TabsTrigger value="upload">Загрузить файл</TabsTrigger>
            </TabsList>

            <div className="flex gap-2">
              <Button type="button" variant="outline" className="gap-2" onClick={() => setFullResumeOpen(true)}>
                <FileText className="w-4 h-4" />
                Полное резюме
              </Button>
              <Button onClick={handleSave} className="gap-2">
              {isSaved ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Сохранено
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Сохранить
                </>
              )}
            </Button>
            </div>
          </div>

          <TabsContent value="edit" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Основная информация */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="w-5 h-5 text-primary" />
                    Основная информация
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">ФИО</Label>
                    <Input
                      id="fullName"
                      value={resume.fullName}
                      onChange={(e) => setResume(prev => ({ ...prev, fullName: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="position">Желаемая должность</Label>
                    <Input
                      id="position"
                      value={resume.position}
                      onChange={(e) => setResume(prev => ({ ...prev, position: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="title">Заголовок резюме</Label>
                    <Input
                      id="title"
                      value={resume.title}
                      onChange={(e) => setResume(prev => ({ ...prev, title: e.target.value }))}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Контакты */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mail className="w-5 h-5 text-primary" />
                    Контакты
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="flex items-center gap-2">
                      <Mail className="w-4 h-4" /> Email
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={resume.contacts.email || ''}
                      onChange={(e) => setResume(prev => ({ 
                        ...prev, 
                        contacts: { ...prev.contacts, email: e.target.value }
                      }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone" className="flex items-center gap-2">
                      <Phone className="w-4 h-4" /> Телефон
                    </Label>
                    <Input
                      id="phone"
                      value={resume.contacts.phone || ''}
                      onChange={(e) => setResume(prev => ({ 
                        ...prev, 
                        contacts: { ...prev.contacts, phone: e.target.value }
                      }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="telegram" className="flex items-center gap-2">
                      <MessageCircle className="w-4 h-4" /> Telegram
                    </Label>
                    <Input
                      id="telegram"
                      value={resume.contacts.telegram || ''}
                      onChange={(e) => setResume(prev => ({ 
                        ...prev, 
                        contacts: { ...prev.contacts, telegram: e.target.value }
                      }))}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Опыт работы */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-primary" />
                    Опыт работы
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={resume.experience}
                    onChange={(e) => setResume(prev => ({ ...prev, experience: e.target.value }))}
                    className="min-h-[200px]"
                    placeholder="Опишите ваш опыт работы..."
                  />
                </CardContent>
              </Card>

              {/* Образование */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <GraduationCap className="w-5 h-5 text-primary" />
                    Образование
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={resume.education}
                    onChange={(e) => setResume(prev => ({ ...prev, education: e.target.value }))}
                    className="min-h-[120px]"
                    placeholder="Укажите ваше образование..."
                  />
                </CardContent>
              </Card>

              {/* Навыки */}
              <Card className="border-border/50 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="w-5 h-5 text-primary" />
                    Навыки
                  </CardTitle>
                  <CardDescription>
                    Добавьте навыки, которые будут использоваться при анализе вакансий
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      placeholder="Добавить навык..."
                      onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                    />
                    <Button onClick={handleAddSkill} variant="outline">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {resume.skills.map((skill) => (
                      <Badge 
                        key={skill} 
                        variant="secondary"
                        className="gap-1 pr-1"
                      >
                        {skill}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-4 w-4 hover:bg-destructive/20"
                          onClick={() => handleRemoveSkill(skill)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* О себе */}
              <Card className="border-border/50 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    О себе
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={resume.about}
                    onChange={(e) => setResume(prev => ({ ...prev, about: e.target.value }))}
                    className="min-h-[150px]"
                    placeholder="Расскажите о себе..."
                  />
                </CardContent>
              </Card>

              <Card className="border-border/50 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="w-5 h-5 text-primary" />
                    Текст из файла (черновик)
                  </CardTitle>
                  <CardDescription>
                    Сюда попадает текст из PDF / DOCX / TXT; используется в полном резюме и для LLM
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={resume.rawText}
                    onChange={(e) => setResume((prev) => ({ ...prev, rawText: e.target.value }))}
                    className="min-h-[200px] font-mono text-sm"
                    placeholder="Загрузите файл на вкладке «Загрузить файл» или вставьте текст вручную…"
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="preview">
            <Card className="border-border/50 max-w-3xl mx-auto">
              <CardContent className="p-8">
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold mb-2">{resume.fullName}</h1>
                  <p className="text-xl text-primary">{resume.position}</p>
                </div>

                <div className="flex justify-center gap-6 mb-8 text-sm text-muted-foreground">
                  {resume.contacts.email && (
                    <span className="flex items-center gap-1">
                      <Mail className="w-4 h-4" />
                      {resume.contacts.email}
                    </span>
                  )}
                  {resume.contacts.phone && (
                    <span className="flex items-center gap-1">
                      <Phone className="w-4 h-4" />
                      {resume.contacts.phone}
                    </span>
                  )}
                  {resume.contacts.telegram && (
                    <span className="flex items-center gap-1">
                      <MessageCircle className="w-4 h-4" />
                      {resume.contacts.telegram}
                    </span>
                  )}
                </div>

                <div className="space-y-6">
                  {resume.about && (
                    <section>
                      <h2 className="text-lg font-semibold border-b pb-2 mb-3">О себе</h2>
                      <p className="text-muted-foreground leading-relaxed">{resume.about}</p>
                    </section>
                  )}

                  <section>
                    <h2 className="text-lg font-semibold border-b pb-2 mb-3">Навыки</h2>
                    <div className="flex flex-wrap gap-2">
                      {resume.skills.map((skill) => (
                        <Badge key={skill} variant="outline">{skill}</Badge>
                      ))}
                    </div>
                  </section>

                  <section>
                    <h2 className="text-lg font-semibold border-b pb-2 mb-3">Опыт работы</h2>
                    <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">
                      {resume.experience}
                    </p>
                  </section>

                  <section>
                    <h2 className="text-lg font-semibold border-b pb-2 mb-3">Образование</h2>
                    <p className="text-muted-foreground leading-relaxed">{resume.education}</p>
                  </section>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="upload">
            <Card className="border-border/50 max-w-xl mx-auto">
              <CardHeader>
                <CardTitle>Загрузить резюме из файла</CardTitle>
                <CardDescription>
                  Поддерживаются форматы: PDF, DOCX, TXT (до ~10 МБ)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={UPLOAD_ACCEPT}
                  className="sr-only"
                  disabled={uploadBusy}
                  onChange={(e) => {
                    const f = e.target.files?.[0]
                    e.target.value = ''
                    if (f) void ingestUploadedFile(f)
                  }}
                />
                <div
                  onDragEnter={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setDragOver(true)
                  }}
                  onDragOver={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setDragOver(true)
                  }}
                  onDragLeave={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setDragOver(false)
                  }}
                  onDrop={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setDragOver(false)
                    const f = e.dataTransfer.files?.[0]
                    if (f) void ingestUploadedFile(f)
                  }}
                  className={cn(
                    'border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-ring',
                    dragOver ? 'border-primary bg-primary/5' : 'border-border',
                  )}
                  onClick={() => !uploadBusy && fileInputRef.current?.click()}
                >
                  <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium mb-2">Перетащите файл сюда</p>
                  <p className="text-muted-foreground mb-4">или нажмите для выбора</p>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={uploadBusy}
                    onClick={(ev) => {
                      ev.stopPropagation()
                      fileInputRef.current?.click()
                    }}
                  >
                    {uploadBusy ? 'Обработка…' : 'Выбрать файл'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <Dialog open={fullResumeOpen} onOpenChange={setFullResumeOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Полное резюме (markdown)</DialogTitle>
          </DialogHeader>
          <div className="overflow-y-auto pr-2 text-sm">
            <SafeMarkdown className="[&_h1]:text-xl [&_h1]:font-bold [&_h2]:text-base [&_h2]:font-semibold [&_h2]:mt-4 [&_p]:mb-2">
              {resumeAsMarkdown(resume)}
            </SafeMarkdown>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
