type QueueItem = {
  label: string;
  window: string;
  emphasis: "focus" | "steady" | "later";
};

type RailNote = {
  title: string;
  value: string;
  hint: string;
};

const queue: QueueItem[] = [
  { label: "整理今天的重点待办", window: "09:00 - 10:00", emphasis: "focus" },
  { label: "推进课程笔记补全", window: "11:00 - 12:00", emphasis: "steady" },
  { label: "下班前回看未完成事项", window: "19:30 - 20:00", emphasis: "later" }
];

const notes: RailNote[] = [
  { title: "完成率", value: "0%", hint: "任务数据接入后会替换为真实统计" },
  { title: "今日分区", value: "工作 / 学习 / 生活", hint: "后续接入分类和筛选" },
  { title: "本地状态", value: "ready", hint: "下一任务会接入 IndexedDB 仓储层" }
];

const toneStyles: Record<QueueItem["emphasis"], string> = {
  focus: "text-glow before:bg-glow/80",
  steady: "text-slate-100 before:bg-ember/80",
  later: "text-mist before:bg-mist/75"
};

function App() {
  return (
    <div className="min-h-screen bg-ink text-slate-50">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute left-[10%] top-[-8rem] h-80 w-80 rounded-full bg-glow/10 blur-3xl" />
        <div className="absolute right-[8%] top-[8rem] h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute bottom-[-6rem] left-1/3 h-72 w-72 rounded-full bg-ember/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-[1600px] flex-col px-4 py-4 sm:px-6 lg:px-8">
        <div className="grid flex-1 gap-4 lg:grid-cols-[220px_minmax(0,1fr)_300px]">
          <aside className="animate-rise rounded-[28px] border border-line bg-shell/70 p-5 shadow-panel backdrop-blur motion-reduce:animate-none">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.32em] text-mist">
                  Dayboard
                </p>
                <h1 className="mt-3 text-2xl font-semibold tracking-tight text-slate-50">
                  今日计划
                </h1>
              </div>
              <div className="h-3 w-3 animate-drift rounded-full bg-glow shadow-[0_0_18px_rgba(154,230,180,0.8)] motion-reduce:animate-none" />
            </div>

            <nav className="mt-10 space-y-2 text-sm text-mist">
              {["今日清单", "历史回看", "分类视图", "本地数据"].map((item, index) => (
                <button
                  key={item}
                  type="button"
                  className={`group flex w-full items-center justify-between rounded-2xl px-3 py-3 text-left transition ${
                    index === 0
                      ? "bg-white/8 text-slate-50"
                      : "hover:bg-white/5 hover:text-slate-100"
                  }`}
                >
                  <span>{item}</span>
                  <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-mist transition group-hover:text-slate-200">
                    {index === 0 ? "live" : "soon"}
                  </span>
                </button>
              ))}
            </nav>

            <div className="mt-10 border-t border-line pt-5">
              <p className="font-mono text-xs uppercase tracking-[0.28em] text-mist">
                Shell Focus
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                当前阶段先交付稳定的应用骨架、结构化布局和基础视觉体系，后续任务再接入真实任务数据。
              </p>
            </div>
          </aside>

          <main className="animate-rise rounded-[32px] border border-line bg-white/[0.035] p-5 shadow-panel backdrop-blur [animation-delay:120ms] motion-reduce:animate-none sm:p-7">
            <header className="flex flex-col gap-5 border-b border-line pb-6 md:flex-row md:items-end md:justify-between">
              <div className="max-w-2xl">
                <p className="font-mono text-xs uppercase tracking-[0.34em] text-mist">
                  Personal Daily Planner
                </p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                  一个从今天开始就能使用的个人任务工作台
                </h2>
                <p className="mt-3 max-w-xl text-sm leading-7 text-slate-300 sm:text-base">
                  当前应用壳聚焦今天的主工作区、任务队列预览和右侧上下文信息。真实 CRUD、分类和统计会按后续任务逐步接入。
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  className="rounded-full border border-glow/40 bg-glow/10 px-5 py-2.5 text-sm font-medium text-glow transition hover:bg-glow/15"
                >
                  新建今日事项
                </button>
                <button
                  type="button"
                  className="rounded-full border border-line px-5 py-2.5 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:bg-white/5"
                >
                  查看历史
                </button>
              </div>
            </header>

            <section className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,1fr)_240px]">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-mono text-xs uppercase tracking-[0.28em] text-mist">
                      Today Queue
                    </p>
                    <p className="mt-2 text-lg font-medium text-slate-100">
                      主工作区预览
                    </p>
                  </div>
                  <p className="text-sm text-mist">默认按今天优先展示</p>
                </div>

                <div className="overflow-hidden rounded-[28px] border border-line bg-shell/65">
                  {queue.map((item) => (
                    <article
                      key={item.label}
                      className="group flex flex-col gap-3 border-b border-line px-5 py-5 last:border-b-0 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div className={`relative pl-5 before:absolute before:left-0 before:top-2 before:h-2.5 before:w-2.5 before:rounded-full ${toneStyles[item.emphasis]}`}>
                        <p className="text-base font-medium tracking-tight sm:text-lg">
                          {item.label}
                        </p>
                        <p className="mt-1 text-sm text-mist">
                          应用壳阶段使用静态占位数据，下一任务会切换为真实列表。
                        </p>
                      </div>

                      <div className="flex items-center gap-3 text-sm text-slate-300">
                        <span className="rounded-full border border-line px-3 py-1 font-mono text-xs uppercase tracking-[0.22em] text-mist">
                          {item.window}
                        </span>
                        <button
                          type="button"
                          className="rounded-full border border-line px-4 py-2 transition group-hover:border-slate-500 group-hover:bg-white/5"
                        >
                          编辑
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              <div className="rounded-[28px] border border-line bg-shell/55 p-5">
                <p className="font-mono text-xs uppercase tracking-[0.28em] text-mist">
                  Build Scope
                </p>
                <ul className="mt-4 space-y-4 text-sm text-slate-300">
                  <li className="border-b border-line pb-4">
                    React + TypeScript + Vite 已作为前端骨架。
                  </li>
                  <li className="border-b border-line pb-4">
                    Tailwind 已接入，并用于当前页面布局与主题样式。
                  </li>
                  <li>
                    本地数据层将在下一任务落地，避免当前壳层过早绑定存储细节。
                  </li>
                </ul>
              </div>
            </section>
          </main>

          <aside className="animate-rise rounded-[28px] border border-line bg-shell/70 p-5 shadow-panel backdrop-blur [animation-delay:220ms] motion-reduce:animate-none">
            <div className="border-b border-line pb-5">
              <p className="font-mono text-xs uppercase tracking-[0.3em] text-mist">
                Context Rail
              </p>
              <h3 className="mt-3 text-xl font-semibold tracking-tight text-slate-50">
                今日概览
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                右侧区域保留给统计、筛选提示和本地状态。先交付稳定结构，再接入真实数据。
              </p>
            </div>

            <div className="mt-5 space-y-5">
              {notes.map((note) => (
                <section key={note.title} className="border-b border-line pb-5 last:border-b-0 last:pb-0">
                  <p className="text-sm text-mist">{note.title}</p>
                  <p className="mt-2 text-2xl font-semibold tracking-tight text-white">
                    {note.value}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {note.hint}
                  </p>
                </section>
              ))}
            </div>

            <div className="mt-8 rounded-[24px] border border-white/8 bg-white/[0.03] p-4">
              <p className="font-mono text-xs uppercase tracking-[0.3em] text-mist">
                Next Contract
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                T002 会补齐任务实体、分类与优先级字段，并把当前静态占位内容替换为本地仓储读取结果。
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default App;
