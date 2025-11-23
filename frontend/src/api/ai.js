import request from './request'

/**
 * AI分析相关API
 */

/**
 * 执行AI工作分析
 * @param {Object} params - 分析参数
 * @param {number} params.user_id - 用户ID（可选，为空则分析团队）
 * @param {string} params.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期 (YYYY-MM-DD)
 * @param {string} params.analysis_type - 分析类型: comprehensive, performance, improvement
 * @returns {Promise} 分析结果
 */
export function analyzeWork(params) {
  return request({
    url: '/ai/analyze',
    method: 'post',
    data: params,
    timeout: 60000 // AI分析可能需要较长时间，设置60秒超时
  })
}

/**
 * 获取AI分析历史记录
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页条数
 * @param {string} params.start_date - 开始日期筛选
 * @param {string} params.end_date - 结束日期筛选
 * @returns {Promise} 分析历史列表
 */
export function getAnalysisHistory(params) {
  return request({
    url: '/ai/analyses',
    method: 'get',
    params
  })
}

/**
 * 获取单个AI分析详情
 * @param {number} id - 分析记录ID
 * @returns {Promise} 分析详情
 */
export function getAnalysisDetail(id) {
  return request({
    url: `/ai/analyses/${id}`,
    method: 'get'
  })
}

/**
 * 删除AI分析记录
 * @param {number} id - 分析记录ID
 * @returns {Promise} 删除结果
 */
export function deleteAnalysis(id) {
  return request({
    url: `/ai/analyses/${id}`,
    method: 'delete'
  })
}

/**
 * 检查AI服务状态
 * @returns {Promise} 服务状态
 */
export function checkAIStatus() {
  return request({
    url: '/ai/status',
    method: 'get'
  })
}