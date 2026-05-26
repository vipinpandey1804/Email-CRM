interface Props {
  subjectLine: string
  onSubjectChange: (value: string) => void
}

export default function SubjectLineBar({ subjectLine, onSubjectChange }: Props) {
  const charCount = subjectLine.length
  const isLong = charCount > 60
  const isOverLimit = charCount > 300

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-card border-b border-border">
      <span className="text-xs text-muted-foreground whitespace-nowrap">Subject:</span>
      <input
        value={subjectLine}
        onChange={(e) => onSubjectChange(e.target.value)}
        className="flex-1 bg-transparent text-foreground text-sm focus:outline-none placeholder:text-muted-foreground"
        placeholder="Enter subject line..."
        maxLength={300}
      />
      <span
        className={`text-xs whitespace-nowrap ${
          isOverLimit ? 'text-destructive' : isLong ? 'text-yellow-400' : 'text-muted-foreground'
        }`}
      >
        {charCount}/300
      </span>
      {isLong && (
        <span className="text-xs text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded">Long</span>
      )}
    </div>
  )
}
