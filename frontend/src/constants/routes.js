export const routeNames = {
  login: 'login',
  home: 'home',
  detective: 'detective',
  result: 'result',
  history: 'history',
  historyDetail: 'historyDetail'
}

export const navigationItems = [
  { name: routeNames.home, path: '/', label: '首页', icon: 'H' },
  { name: routeNames.detective, path: '/detective', label: '图片检测', icon: 'D' },
  { name: routeNames.history, path: '/history', label: '历史记录', icon: 'R' }
]
