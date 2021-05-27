% l = locals()
<div class="btn-group" id="queue-button">
  <button class="btn btn-info btn-sm dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      {{!system.queue_badge() if "system" in l else blog.queue_badge()}} Queue
  </button>
  <div class="dropdown-menu dropdown-menu-right">
    % if "system" in l:
    <a class="dropdown-item" href="#">System queue</a>
    <a class="dropdown-item" href="#">Republish all blogs</a>
    % else:      
      % queue_id = None
      % if "post" in l:
        % queue_id = post.blog.id      
      % elif "blog" in l:
        % queue_id = blog.id
      % end
      % if queue_id:
        <script src="/static/js/queue.js"></script>
        <script>var blog_id = "{{queue_id}}"; window.setInterval(refreshQueue, 60000);</script>
        <a class="dropdown-item" href="#" onclick="refreshQueue()">Refresh queue count</a>  
      % end
    <a class="dropdown-item" href="{{blog.queue_manage_link}}">See blog queue</a>
    <a class="dropdown-item" target="_blank" href="{{blog.manage_link}}/runqueue">Run queue manually →</a>
    % end
  </div>
</div>