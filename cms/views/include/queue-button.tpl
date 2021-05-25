<div class="btn-group" id="queue-button">
    <button class="btn btn-info btn-sm dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true"
      aria-expanded="false">
      {{!system.queue_badge() if "system" in locals() else blog.queue_badge()}}
      Queue
    </button>
    <div class="dropdown-menu dropdown-menu-right">
      % if "system" in locals():
      <a class="dropdown-item" href="#">System queue</a>
      <a class="dropdown-item" href="#">Republish all blogs</a>
      % else:
      <a class="dropdown-item" href="{{blog.queue_manage_link}}">See blog queue</a>
      <a class="dropdown-item" target="_blank" href="{{blog.manage_link}}/runqueue">Run queue manually →</a>
      % end
    </div>
</div>